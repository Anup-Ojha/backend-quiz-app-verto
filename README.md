# 🐍 FastAPI Quiz Backend

This repository contains the backend API for a simple multiple-choice quiz application. It is built using FastAPI for high performance, SQLAlchemy for database operations, and utilizes a local SQLite database for persistent question storage.

---

## 🚀 Setup and Installation

Follow these steps to get your project environment set up and the application running locally.

## 1\. Prerequisites

* Python 3.8+ must be installed.

## 2\. Clone the Repository

bash

`git clone <your-repository-url`

`
cd <your-repository-name>
`

## 3\. Virtual Environment Setup (Best Practice)

Isolate your project dependencies with a virtual environment.

## A. Troubleshooting Existing `venv` ⚠️

If you face dependency issues (such as copying the `venv` folder from a different OS or setup), remove the existing one and generate a fresh environment.

bash

`# Delete the old virtual environment
rm -rf venv 
# Create a new virtual environment
python -m venv venv
`

## B. Activate the Environment

You must activate the environment before installing dependencies.

bash

# On macOS/Linux
`
source venv/bin/activate
`
# On Windows (Command Prompt/PowerShell)
`
source venv/Scripts/activate
`

> **Note:** The core dependencies are FastAPI, Uvicorn, SQLAlchemy, and Pydantic. This command installs everything needed.

## 4\. Database Initialization (SQLite) 💾

* SQLite is included with Python and requires no separate installation.
* On first run:  
   * The `app/core/database.py` script auto-creates an `anup.db` file.  
   * It sets up the `questions` table.  
   * It seeds the initial quiz data.

## 5\. Run the Application

Start the FastAPI server using Uvicorn with the `--reload` flag for development:

bash

`uvicorn app.main:app --reload
`

## 6\. Install Only if The App doesn't work else i have added all of the deatils into the repo with lib also and make a new venv for any problems 

Install all required packages listed in `requirements.txt`.

bash

`pip install -r requirements.txt
`

* Server: <http://127.0.0.1:8000/>

* For Testing and API testing you can also use this Swagger Dosc which is available by using the below link or you can use postman also 
* Interactive API docs (Swagger UI): <http://127.0.0.1:8000/docs>

---

## 💻 API Endpoints

| Method | URL                            | Description                                                                                                 |
| ------ | ------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| GET    | /topics                        | Fetches a list of all unique quiz topics.                                                                   |
| GET    | /quizzes/start/{topic\_name}   | Retrieves all questions for the specified topic (without correct answers).                                  |
| POST   | /quizzes/submit                | Accepts user answers, calculates the score in real time, returns result (no permanent storage of attempts). |
| GET    | /quizzes/results/{topic\_name} | Fetches all questions for a topic, including the correct answers, for result review.                        |

---

If you encounter virtual environment or dependency issues, remove and recreate the `venv` folder as described above.
