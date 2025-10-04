# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Setup ---
# Configuration to use a SQLite file named 'anup.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./anup.db"

# Create the engine, necessary for SQLite in multi-threaded environments (like FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Configure a SessionLocal class to create sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models (all models inherit from this)
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get a database session.
    It ensures the session is always closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_database():
    """
    Initializes the database: creates tables if they don't exist,
    and seeds initial quiz data if the Question table is empty.
    """
    # Import models to ensure they are registered with Base.metadata
    from app.models import models
    # Create tables defined in the models file
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from app.models.models import Question

        # Check if dummy data already exists
        if db.query(Question).count() > 0:
            print("Dummy quiz data already exists. Skipping insertion.")
            return

        # Data structure for seeding questions (Topic: [Question, OptA, OptB, OptC, OptD, CorrectKey])
        question_data = {
            "General Knowledge": [
                ("What is the largest planet in our solar system?", "Jupiter", "Mars", "Earth", "Venus", "A"),
                ("What is the process by which plants make their own food?", "Respiration", "Photosynthesis", "Digestion", "Transpiration", "B"),
                ("Which country gifted the Statue of Liberty to the US?", "Germany", "UK", "France", "Italy", "C"),
                ("How many continents are there?", "Five", "Six", "Four", "Seven", "D"),
                ("What is the chemical symbol for water?", "H2O", "O2", "CO2", "NaCl", "A"),
            ],
            "Geography": [
                ("What is the capital of France?", "Paris", "Rome", "Berlin", "Madrid", "A"),
                ("Which ocean is the largest?", "Atlantic Ocean", "Pacific Ocean", "Indian Ocean", "Arctic Ocean", "B"),
                ("Mount Everest is located in which mountain range?", "Andes", "Alps", "Himalayas", "Rockies", "C"),
                ("The river Nile flows into which sea?", "Red Sea", "Black Sea", "Aral Sea", "Mediterranean Sea", "D"),
                ("The Great Barrier Reef is off the coast of which country?", "Australia", "Brazil", "Mexico", "South Africa", "A"),
            ],
            "DSA": [
                ("Which structure is LIFO (Last-In, First-Out)?", "Queue", "Stack", "Array", "Linked List", "B"),
                ("What is the time complexity for accessing an element in an array by index?", "O(1)", "O(n)", "O(log n)", "O(n^2)", "A"),
                ("A Queue is known for which order of access?", "LIFO", "FILO", "FIFO", "Random", "C"),
                ("Which data structure uses nodes and pointers?", "Array", "Stack", "Heap", "Linked List", "D"),
                ("An algorithm's efficiency is primarily measured by time and what else?", "Cost", "Space", "Power", "Readability", "B"),
            ],
            "Python": [
                ("Which keyword is used to define a function in Python?", "func", "define", "def", "function", "C"),
                ("What is the file extension for a Python source file?", ".py", ".p", ".pyt", ".python", "A"),
                ("Which method adds an element to the end of a list?", "insert()", "add()", "extend()", "append()", "D"),
                ("In Python, which loop is used to iterate over a sequence?", "while", "for", "do-while", "loop", "B"),
                ("What is the output of '2' + '3' in Python?", "'23'", "5", "Error", "'5'", "A"),
            ],
            "SQL": [
                ("Which SQL statement is used to retrieve data from a database?", "SELECT", "GET", "RETRIEVE", "EXTRACT", "A"),
                ("Which clause is used to filter records in SQL?", "HAVING", "WHERE", "FILTER", "ORDER BY", "B"),
                ("Which SQL statement is used to delete data?", "REMOVE", "DROP", "DELETE", "CLEAR", "C"),
                ("Which SQL keyword is used to sort the result-set?", "SORT BY", "GROUP BY", "ARRANGE", "ORDER BY", "D"),
                ("Which SQL function is used to count the number of rows?", "COUNT()", "SUM()", "TOTAL()", "NUMBER()", "A"),
            ],
        }

        for topic_name, questions in question_data.items():
            for q_text, opt_a, opt_b, opt_c, opt_d, correct_key in questions:
                # Check for existing question to prevent duplicates on subsequent runs if DB was edited manually
                existing_q = db.query(Question).filter(
                    Question.topic_name == topic_name,
                    Question.text == q_text
                ).first()

                if not existing_q:
                    new_question = Question(
                        topic_name=topic_name,
                        text=q_text,
                        option_a=opt_a,
                        option_b=opt_b,
                        option_c=opt_c,
                        option_d=opt_d,
                        correct_answer_key=correct_key
                    )
                    db.add(new_question)
                    print(f"Adding question for {topic_name}: {q_text[:60]}")

        db.commit()
        print("✅ Dummy quiz data inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during setup: {e}")
    finally:
        db.close()


# Run setup when this module is imported (seeds data only if DB is empty)
setup_database()