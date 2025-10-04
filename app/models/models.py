from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from app.core.database import Base 

class Question(Base):

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    # NEW: Store topic name directly instead of using a ForeignKey
    topic_name = Column(String, index=True, nullable=False) 
    
    text = Column(String, index=True, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    
    correct_answer_key = Column(String, nullable=False)

    submissions = relationship("UserAttempt", back_populates="question") 

    def __repr__(self):
        return f"<Question(topic='{self.topic_name}', text='{self.text[:30]}...')>"


class UserAttempt(Base):

    __tablename__ = "user_attempts"

    id = Column(Integer, primary_key=True, index=True)

    attempt_id = Column(Integer, index=True, nullable=False) 
    
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    submitted_answer_key = Column(String, nullable=False) 
    is_correct = Column(Integer) # 1 for True, 0 for False
    
    question = relationship("Question", back_populates="submissions")

    def __repr__(self):
        return f"<UserAttempt(attempt_id={self.attempt_id}, question_id={self.question_id})>"

