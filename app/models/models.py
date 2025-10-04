
from sqlalchemy import Column, Integer, String
from app.core.database import Base 

class Question(Base):

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, index=True, nullable=False) 
    
    text = Column(String, index=True, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    
    correct_answer_key = Column(String, nullable=False)


    def __repr__(self):
        return f"<Question(topic='{self.topic_name}', text='{self.text[:30]}...')>"

