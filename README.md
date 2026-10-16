## Library Circulation Management

LibraFlow is a full-stack library management application built with Python, FastAPI, SQLAlchemy, SQLite, Alembic, HTML, CSS, and vanilla JavaScript.

### Features

**Book Management**
- Add and list books
- Edit book information
- Archive books without deleting historical records
- Track total and available copies

**Member Management**
- Register members
- Edit member details
- Deactivate member accounts
- Prevent duplicate member email addresses

**Loan Management**
- Issue books to active members
- Validate book availability before borrowing
- Automatically decrease available inventory when borrowing
- Return books and restore available inventory
- Prevent double returns
- View active and returned loans
- Track borrowing and due dates
- Identify overdue loans
- Search and filter borrowing history

### Backend Architecture

The backend follows a modular structure:

- `api/` — FastAPI route handlers
- `models/` — SQLAlchemy database models
- `schemas/` — Pydantic request and response schemas
- `services/` — Business logic and database transactions
- `db/` — Database configuration and sessions
- `migrations/` — Alembic database migrations
- `tests/` — Automated tests using pytest

### Running Locally

From the `backend` directory, create and activate a Python virtual environment.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Apply database migrations:

```powershell
python -m alembic upgrade head
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Open the application at `http://127.0.0.1:8000/`.

API documentation is available at `http://127.0.0.1:8000/docs`.

### Running Tests

From the `backend` directory:

```powershell
python -m pytest -v
```

Tests use an isolated SQLite database and do not require access to the application's normal database.

### Current Scope

LibraFlow is currently designed for local development and learning. Authentication, role-based authorization, and production deployment configuration are not yet implemented.
