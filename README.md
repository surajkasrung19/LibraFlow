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

### Library Circulation Policies

LibraFlow includes configurable rules for borrowing and renewing library books.

**Borrowing limits**

- Members have a configurable maximum number of simultaneous active loans.

- Returned books no longer count toward the active borrowing limit.

- Borrowing requests that exceed the limit are rejected.

**Overdue restrictions**

- Members with overdue loans cannot borrow additional books.

- Returning overdue books removes the restriction when no other overdue loans remain.

- Overdue status is derived from the loan's status and due date.

**Loan renewals**

- Eligible active loans can be renewed to extend their due date.

- Renewal limits are configurable.

- Returned and overdue loans cannot be renewed.

- Renewing a loan does not alter book inventory.

## Library Policy Configuration

The backend uses Pydantic Settings and supports these environment variables:

**Environment variable         Default   Description**
______________________________________________________________________________________
LIBRAFLOW_MAX_ACTIVE_LOANS     3         Maximum simultaneous active loans per member
______________________________________________________________________________________
LIBRAFLOW_LOAN_PERIOD_DAYS     14        Loan period and renewal extension in days
______________________________________________________________________________________
LIBRAFLOW_MAX_LOAN_RENEWALS    1         Maximum renewals allowed per loan

- Restart the application after changing environment variables.

**Renewal API**

- PATCH /api/v1/loans/{loan_id}/renew

- Extends the due date of an eligible active loan and increments its renewal count.

- The endpoint returns an updated loan record. Business-rule violations return an HTTP conflict response.


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
