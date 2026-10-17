import pytest
from sqlalchemy import select


from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan
from app.schemas.loan import LoanCreate
from app.services.loan_service import LoanService
from app.services.exceptions import LoanError


def test_create_loan(db_session):
    # Arrange: Add an active member
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.loans@example.com",
        is_active=True
    )

    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=2,
        available_copies=2,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    # Act
    service = LoanService(db_session)

    loan = service.create_loan(
        LoanCreate(
            member_id=member.id,
            book_id=book.id
        )
    )

    # Assert
    assert loan.status == "borrowed"
    assert loan.returned_at is None
    assert loan.member_id == member.id
    assert loan.book_id == book.id

    db_session.refresh(book)

    assert book.available_copies == 1


def test_borrow_when_no_copies_available(db_session):
    # Arrange: Create an active member
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.loans@example.com",
        is_active=True
    )

    # Create a book with zero available copies
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=1,
        available_copies=0,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    # Capture IDs before the service may roll back
    member_id = member.id
    book_id = book.id

    service = LoanService(db_session)

    loan_data = LoanCreate(
        member_id=member_id,
        book_id=book_id
    )

    # Act & Assert: Borrowing must fail
    with pytest.raises(LoanError, match="No available copies"):
        service.create_loan(loan_data)

    # Verify the inventory remains unchanged
    db_session.expire_all()

    saved_book = db_session.get(Book, book_id)

    assert saved_book.available_copies == 0

    # Verify no loan was created
    loans = db_session.scalars(
        select(Loan).where(
            Loan.member_id == member_id,
            Loan.book_id == book_id
        )
    ).all()

    assert len(loans) == 0


def test_return_loan(db_session):
    # Arrange
    member = Member(
        full_name="Priya Sharma",
        email="priya.return@example.com",
        is_active=True
    )

    book = Book(
        title="Atomic Habits",
        author="James Clear",
        isbn="9780735211292",
        total_copies=3,
        available_copies=3,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    member_id = member.id
    book_id = book.id

    service = LoanService(db_session)

    # Borrow one copy
    loan = service.create_loan(
        LoanCreate(member_id=member_id, book_id=book_id)
    )

    assert loan.status == "borrowed"

    db_session.refresh(book)
    assert book.available_copies == 2

    # Act: Return the borrowed book
    returned_loan = service.return_loan(loan.id)

    # Assert: Loan has been returned
    assert returned_loan.status == "returned"
    assert returned_loan.returned_at is not None

    # Assert: Inventory has been restored
    db_session.refresh(book)
    assert book.available_copies == 3


def test_cannot_return_same_loan_twice(db_session):
    # Arrange
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.double@example.com",
        is_active=True
    )

    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=2,
        available_copies=2,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    service = LoanService(db_session)

    # Borrow one copy
    loan = service.create_loan(
        LoanCreate(
            member_id=member.id,
            book_id=book.id
        )
    )

    loan_id = loan.id

    db_session.refresh(book)
    assert book.available_copies == 1

    # Act: First return
    first_return = service.return_loan(loan_id)

    assert first_return.status == "returned"
    assert first_return.returned_at is not None

    db_session.refresh(book)
    assert book.available_copies == 2

    # Act: Return the same loan again
    second_return = service.return_loan(loan_id)

    # Assert: Loan remains returned
    assert second_return.status == "returned"

    # Assert: Inventory wasn't increased twice
    db_session.refresh(book)
    assert book.available_copies == 2

    # Only one loan record should exist
    loans = db_session.scalars(
        select(Loan).where(Loan.book_id == book.id)
    ).all()

    assert len(loans) == 1


def test_return_nonexistent_loan(db_session):
    service = LoanService(db_session)

    with pytest.raises(LoanError, match="Loan not found"):
        service.return_loan(99999)

def test_return_rollback_when_inventory_full(db_session):
    # Arrange: Create a member and book
    member = Member(
        full_name="Priya Sharma",
        email="priya.rollback@example.com",
        is_active=True
    )

    book = Book(
        title="Atomic Habits",
        author="James Clear",
        isbn="9780735211292",
        total_copies=2,
        available_copies=2,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    service = LoanService(db_session)

    # First create a valid borrowed loan
    loan = service.create_loan(
        LoanCreate(
            member_id=member.id,
            book_id=book.id
        )
    )

    loan_id = loan.id
    book_id = book.id

    db_session.refresh(book)
    assert book.available_copies == 1

    # Simulate inconsistent inventory state
    book.available_copies = 2
    db_session.commit()

    # Act: Attempt to return the loan
    with pytest.raises(
        LoanError,
        match="Unable to restore book inventory"
    ):
        service.return_loan(loan_id)

    # Verify rollback preserved the borrowed state
    db_session.expire_all()

    saved_loan = db_session.get(Loan, loan_id)
    saved_book = db_session.get(Book, book_id)

    assert saved_loan.status == "borrowed"
    assert saved_loan.returned_at is None
    assert saved_book.available_copies == 2


def test_borrow_and_return_api(client):
    # Arrange: Create member through API
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul.api@example.com"
        }
    )

    assert member_response.status_code == 201

    member_id = member_response.json()["id"]

    # Create book through API
    book_response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "total_copies": 2
        }
    )

    assert book_response.status_code == 201

    book_id = book_response.json()["id"]

    # Act: Borrow
    borrow_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": member_id,
            "book_id": book_id
        }
    )

    assert borrow_response.status_code == 201

    loan_data = borrow_response.json()
    loan_id = loan_data["id"]

    assert loan_data["status"] == "borrowed"

    # Verify inventory decreased
    book_after_borrow = client.get(
        f"/api/v1/books/{book_id}"
    ).json()

    assert book_after_borrow["available_copies"] == 1

    # Act: Return
    return_response = client.patch(
        f"/api/v1/loans/{loan_id}/return"
    )

    assert return_response.status_code == 200
    assert return_response.json()["status"] == "returned"
    assert return_response.json()["returned_at"] is not None

    # Verify inventory restored
    book_after_return = client.get(
        f"/api/v1/books/{book_id}"
    ).json()

    assert book_after_return["available_copies"] == 2


#Borrowing when no copies are available
def test_borrow_unavailable_book_api(client):
    # ARRANGE: Register a member
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul.unavailable@example.com"
        }
    )

    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    # Create a book with only one copy
    book_response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "total_copies": 1
        }
    )

    assert book_response.status_code == 201
    book_id = book_response.json()["id"]

    loan_payload = {
        "member_id": member_id,
        "book_id": book_id
    }

    # ACT: First borrowing request
    first_borrow = client.post(
        "/api/v1/loans",
        json=loan_payload
    )

    assert first_borrow.status_code == 201

    # ACT: Attempt to borrow the same book again
    second_borrow = client.post(
        "/api/v1/loans",
        json=loan_payload
    )

    # ASSERT: Second request must fail
    assert second_borrow.status_code == 409
    assert second_borrow.json()["detail"] == "No available copies"

    # Verify inventory remains zero
    book_details = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert book_details.status_code == 200
    assert book_details.json()["available_copies"] == 0

    # Verify only one loan exists
    loans_response = client.get("/api/v1/loans")

    assert loans_response.status_code == 200

    book_loans = [
        loan for loan in loans_response.json()
        if loan["book_id"] == book_id
    ]

    assert len(book_loans) == 1

#Return a nonexistent loan
def test_return_nonexistent_loan_api(client):
    response = client.patch(
        "/api/v1/loans/99999/return"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Loan not found"


#Filter active loans
def test_filter_active_loans_api(client):
    # ARRANGE: Create a member
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Priya Sharma",
            "email": "priya.loans@example.com"
        }
    )

    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    # Create two different books
    books = [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "isbn": "9780735211292",
            "total_copies": 2
        },
        {
            "title": "Fluent Python",
            "author": "Luciano Ramalho",
            "isbn": "9781492056355",
            "total_copies": 2
        }
    ]

    book_ids = []

    for book in books:
        response = client.post(
            "/api/v1/books",
            json=book
        )

        assert response.status_code == 201
        book_ids.append(response.json()["id"])

    # Borrow both books
    first_loan = client.post(
        "/api/v1/loans",
        json={
            "member_id": member_id,
            "book_id": book_ids[0]
        }
    )

    second_loan = client.post(
        "/api/v1/loans",
        json={
            "member_id": member_id,
            "book_id": book_ids[1]
        }
    )

    assert first_loan.status_code == 201
    assert second_loan.status_code == 201

    first_loan_id = first_loan.json()["id"]
    second_loan_id = second_loan.json()["id"]

    # ACT: Return the first book
    return_response = client.patch(
        f"/api/v1/loans/{first_loan_id}/return"
    )

    assert return_response.status_code == 200

    # Request active loans only
    active_response = client.get(
        "/api/v1/loans",
        params={"active_only": "true"}
    )

    # ASSERT
    assert active_response.status_code == 200

    active_loans = active_response.json()

    active_ids = [
        loan["id"]
        for loan in active_loans
    ]

    assert first_loan_id not in active_ids
    assert second_loan_id in active_ids

    assert all(
        loan["status"] == "borrowed"
        for loan in active_loans
    )

    # Confirm complete history still contains both loans
    history_response = client.get("/api/v1/loans")

    assert history_response.status_code == 200

    history_ids = {
        loan["id"] for loan in history_response.json()
    }

    assert first_loan_id in history_ids
    assert second_loan_id in history_ids


#Member borrowing history
def test_member_loan_history_api(client):
    # STEP 1: Register two members
    rahul_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul.history@example.com"
        }
    )

    priya_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Priya Sharma",
            "email": "priya.history@example.com"
        }
    )

    assert rahul_response.status_code == 201
    assert priya_response.status_code == 201

    rahul_id = rahul_response.json()["id"]
    priya_id = priya_response.json()["id"]

    # STEP 2: Create two books
    clean_code_response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "total_copies": 2
        }
    )

    atomic_habits_response = client.post(
        "/api/v1/books",
        json={
            "title": "Atomic Habits",
            "author": "James Clear",
            "isbn": "9780735211292",
            "total_copies": 2
        }
    )

    assert clean_code_response.status_code == 201
    assert atomic_habits_response.status_code == 201

    clean_code_id = clean_code_response.json()["id"]
    atomic_habits_id = atomic_habits_response.json()["id"]

    # STEP 3: Both members borrow a book
    rahul_loan_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": rahul_id,
            "book_id": clean_code_id
        }
    )

    priya_loan_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": priya_id,
            "book_id": atomic_habits_id
        }
    )

    assert rahul_loan_response.status_code == 201
    assert priya_loan_response.status_code == 201

    rahul_loan_id = rahul_loan_response.json()["id"]
    priya_loan_id = priya_loan_response.json()["id"]

    # STEP 4: Retrieve Rahul's loan history
    history_response = client.get(
        f"/api/v1/loans/member/{rahul_id}"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    loan_ids = [loan["id"] for loan in history]

    # Rahul's loan must appear
    assert rahul_loan_id in loan_ids

    # Priya's loan must not appear
    assert priya_loan_id not in loan_ids

    # STEP 5: Rahul returns his book
    return_response = client.patch(
        f"/api/v1/loans/{rahul_loan_id}/return"
    )

    assert return_response.status_code == 200
    assert return_response.json()["status"] == "returned"

    # STEP 6: Retrieve Rahul's history again
    history_after_return = client.get(
        f"/api/v1/loans/member/{rahul_id}"
    )

    assert history_after_return.status_code == 200

    updated_history = history_after_return.json()

    # Find Rahul's specific loan
    returned_loan = next(
        loan for loan in updated_history
        if loan["id"] == rahul_loan_id
    )

    assert returned_loan["status"] == "returned"
    assert returned_loan["returned_at"] is not None

    # Priya's loan must still be excluded
    assert all(
        loan["member_id"] == rahul_id
        for loan in updated_history
    )


def test_member_with_no_loan_history(client):
    # ARRANGE: Register a new member
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Amit Sharma",
            "email": "amit.nohistory@example.com"
        }
    )

    assert member_response.status_code == 201

    member_id = member_response.json()["id"]

    # ACT: Request borrowing history
    history_response = client.get(
        f"/api/v1/loans/member/{member_id}"
    )

    # ASSERT: Member exists, but has no loans
    assert history_response.status_code == 200
    assert history_response.json() == []
