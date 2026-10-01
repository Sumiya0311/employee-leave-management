# Employee & Leave Management System

## Project Overview

The Employee & Leave Management System is a REST API built using FastAPI, Python, SQLAlchemy, and MySQL.

The system provides employee management, department management, authentication, leave management, role-based access control, and reporting features.

## Technologies Used

- Python 3.9+
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Alembic
- JWT Authentication
- Passlib / bcrypt
- Pydantic
- Uvicorn
- python-dotenv

## Project Structure

```text
employee-leave-management/
│
├── app/
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── auth/
│
├── alembic/
├── alembic.ini
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt