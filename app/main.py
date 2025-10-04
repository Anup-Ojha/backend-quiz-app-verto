from typing import List, Dict
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func 
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import setup_database, get_db
from app.models.models import Question, UserAttempt


from pydantic import BaseModel
from typing import List, Dict

class QuestionWithAnswerResponse(BaseModel):
    id: int
    topic_name: str
    text: str
    options: Dict[str, str]
    correctAnswer: str  # <-- Include the correct answer key

class QuizForResultResponse(BaseModel):
    topic_name: str
    questions: List[QuestionWithAnswerResponse]

class QuestionResponse(BaseModel):
    id: int
    topic_name: str
    text: str
    options: Dict[str, str]  

class SubmissionItem(BaseModel):
    question_id: int
    answer_key: str

class SubmissionRequest(BaseModel):
    topic_name: str
    answers: List[SubmissionItem]

class QuizResponse(BaseModel):
    topic_name: str
    questions: List[QuestionResponse]

class UserAttemptResponse(BaseModel):
    attempt_id: int
    question_id: int
    topic_name: str
    question_text: str
    submitted_answer: str
    correct_answer: str
    is_correct: bool

class AllUserAttemptsResponse(BaseModel):
    attempts: List[UserAttemptResponse]
# -------------------------------
# Database & Logic Functions
# -------------------------------

def get_topics_list(db: Session) -> List[str]:
    """Fetch all unique topic names."""
    return [t[0] for t in db.query(Question.topic_name).distinct().all()]

def get_questions_by_topic(db: Session, topic: str) -> List[QuestionResponse]:
    """Fetch all questions for a specific topic without shuffling."""
    questions = db.query(Question).filter(Question.topic_name == topic).all()
    if not questions:
        return []

    sanitized_questions = []
    for q in questions:
        sanitized_questions.append(
            QuestionResponse(
                id=q.id,
                topic_name=q.topic_name,
                text=q.text,
                options={
                    "A": q.option_a,
                    "B": q.option_b,
                    "C": q.option_c,
                    "D": q.option_d
                }
            )
        )
    return sanitized_questions

def get_next_attempt_id(db: Session) -> int:
    """Get next unique attempt ID."""
    max_id = db.query(func.max(UserAttempt.attempt_id)).scalar()
    return (max_id or 0) + 1

def process_quiz_submission(db: Session, topic: str, submission_data: List[SubmissionItem]) -> Dict:
    """Process quiz submission and calculate score."""
    if not submission_data:
        raise HTTPException(status_code=400, detail="No answers provided.")

    # Fetch correct answers from DB
    question_ids = [item.question_id for item in submission_data]
    correct_answers = db.query(Question.id, Question.correct_answer_key)\
                        .filter(Question.id.in_(question_ids)).all()
    correct_map = {q_id: key for q_id, key in correct_answers}

    # Track score and save attempts
    new_attempt_id = get_next_attempt_id(db)
    correct_count = 0
    submissions_to_add = []

    for item in submission_data:
        q_id = item.question_id
        user_answer = item.answer_key.upper()
        correct_key = correct_map.get(q_id)

        is_correct = 1 if correct_key and user_answer == correct_key else 0
        if is_correct:
            correct_count += 1

        submissions_to_add.append(
            UserAttempt(
                attempt_id=new_attempt_id,
                question_id=q_id,
                submitted_answer_key=user_answer,
                is_correct=is_correct
            )
        )

    db.add_all(submissions_to_add)
    db.commit()

    total_questions = len(submission_data)
    return {
        "attempt_id": new_attempt_id,
        "topic": topic,
        "score": correct_count,
        "total_questions": total_questions,
        "percentage": (correct_count / total_questions) * 100 if total_questions else 0
    }

# -------------------------------
# FastAPI App Setup
# -------------------------------
app = FastAPI(title="Quiz Backend for Verto")

setup_database()

origins = [
    "http://localhost:4200",  # Angular dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)




@app.get("/quizzes/results/{topic_name}", response_model=QuizForResultResponse)
def get_quiz_for_results(topic_name: str, db: Session = Depends(get_db)):
    """Return all questions for a topic with correct answers for result display"""
    questions = db.query(Question).filter(Question.topic_name == topic_name).all()
    if not questions:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found or has no questions.")

    questions_with_answers = [
        QuestionWithAnswerResponse(
            id=q.id,
            topic_name=q.topic_name,
            text=q.text,
            options={
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d
            },
            correctAnswer=q.correct_answer_key
        )
        for q in questions
    ]

    return {"topic_name": topic_name, "questions": questions_with_answers}


@app.get("/topics")
def list_topics(db: Session = Depends(get_db)):
    topics = get_topics_list(db)
    return {"topics": topics}

@app.get("/quizzes/start/{topic_name}", response_model=QuizResponse)
def get_quiz_questions(topic_name: str, db: Session = Depends(get_db)):
    questions = get_questions_by_topic(db, topic_name)
    if not questions:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found or has no questions.")
    return {"topic_name": topic_name, "questions": questions}




@app.post("/quizzes/submit")
def submit_quiz(submission: SubmissionRequest, db: Session = Depends(get_db)):
    results = process_quiz_submission(db, submission.topic_name, submission.answers)
    return {
        "message": "Submission recorded successfully. Here are your results:",
        "results": results
    }



