from typing import List, Dict
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import setup_database, get_db
from app.models.models import Question


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
"""Fetch all unique topic names."""
def get_topics_list(db: Session) -> List[str]:
    """Fetch all unique topic names."""
    return [t[0] for t in db.query(Question.topic_name).distinct().all()]

def get_questions_by_topic(db: Session, topic: str) -> List[QuestionResponse]:
    """Fetch all questions for a specific topic."""
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
                    "A": q.option_a, "B": q.option_b,
                    "C": q.option_c, "D": q.option_d
                }
            )
        )
    return sanitized_questions

# Removed: get_next_attempt_id (not needed as we are not saving attempts)


def process_quiz_submission(db: Session, topic: str, submission_data: List[SubmissionItem]) -> Dict:
    """Process quiz submission and calculate score without saving attempts."""
    if not submission_data:
        raise HTTPException(status_code=400, detail="No answers provided.")

    # 1. Fetch correct answers from DB for the submitted question IDs
    question_ids = [item.question_id for item in submission_data]
    correct_answers = db.query(Question.id, Question.correct_answer_key)\
                        .filter(Question.id.in_(question_ids)).all()
    correct_map = {q_id: key for q_id, key in correct_answers}

    # 2. Calculate score
    correct_count = 0

    for item in submission_data:
        q_id = item.question_id
        user_answer = item.answer_key.upper()
        correct_key = correct_map.get(q_id)

        # Score the question
        if correct_key and user_answer == correct_key:
            correct_count += 1
            
    # 3. Return results immediately (no database write/commit needed)
    total_questions = len(submission_data)
    return {
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



