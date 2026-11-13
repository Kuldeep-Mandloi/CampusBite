# CampusBite 🍔

### Restaurant Ordering and Delivery Platform

CampusBite is a restaurant ordering and delivery platform built using Python, FastAPI, SQLAlchemy and SQLite.

## 🚀 Features

- User registration and login
- JWT-based authentication
- Role-based access control
- Restaurant management
- Menu item management
- Customer order placement
- Order total calculation
- Order status management
- Mock payment status

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **API Documentation:** Swagger UI

## 📁 Project Structure

```text
CampusBite/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── add_password_column.py
│   ├── fix_menu_table.py
│   └── fix_orders_table.py
│
├── .gitignore
└── README.md
```

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/Kuldeep-Mandloi/CampusBite.git
```

2. Navigate to the backend:

```bash
cd CampusBite/backend
```

3. Install the required dependencies:

```bash
pip install fastapi uvicorn sqlalchemy python-jose passlib[bcrypt] python-multipart email-validator
```

4. Start the server:

```bash
python -m uvicorn app.main:app --reload
```

## 📖 API Documentation

Open Swagger UI in your browser:

http://127.0.0.1:8000/docs

## 🗄️ Database

CampusBite uses SQLite with SQLAlchemy ORM.

## 👨‍💻 Developer

**Kuldeep Mandloi**

GitHub: https://github.com/Kuldeep-Mandloi

## 📌 Project Status

Backend MVP developed for capstone project submission.