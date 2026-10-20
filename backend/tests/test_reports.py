from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan

from datetime import datetime, timedelta, timezone


def test_library_overview_with_data(client, db_session):
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="REPORT-001",
        total_copies=5,
        available_copies=4,
        is_active=True
    )

    member = Member(
        full_name="Rahul Sharma",
        email="rahul.reports@example.com",
        is_active=True
    )

    db_session.add_all([book, member])
    db_session.commit()

    now = datetime.now(timezone.utc)

    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        borrowed_at=now,
        due_at=now + timedelta(days=14),
        status="borrowed",
        renewal_count=0
    )

    db_session.add(loan)
    db_session.commit()

    response = client.get("/api/v1/reports/overview")

    assert response.status_code == 200

    data = response.json()

    assert data["total_book_titles"] == 1
    assert data["total_book_copies"] == 5
    assert data["available_book_copies"] == 4
    assert data["borrowed_book_copies"] == 1
    assert data["active_loans"] == 1
    assert data["active_members"] == 1
    assert data["returned_loans"] == 0
    assert data["overdue_loans"] == 0

def test_inventory_audit_consistent(client, db_session):
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="AUDIT-001",
        total_copies=3,
        available_copies=3,
        is_active=True
    )

    db_session.add(book)
    db_session.commit()

    response = client.get("/api/v1/reports/inventory-audit")

    assert response.status_code == 200

    data = response.json()

    assert data["total_books_checked"] == 1
    assert data["mismatched_books"] == 0
    assert data["is_consistent"] is True
    assert data["mismatches"] == []

def test_inventory_audit_detects_mismatch(client, db_session):
    book = Book(
        title="Atomic Habits",
        author="James Clear",
        isbn="AUDIT-002",
        total_copies=4,
        available_copies=2,
        is_active=True
    )

    db_session.add(book)
    db_session.commit()

    # Inventory claims two copies are borrowed,
    # but no active Loan records exist.

    response = client.get("/api/v1/reports/inventory-audit")

    assert response.status_code == 200

    data = response.json()

    assert data["total_books_checked"] == 1
    assert data["mismatched_books"] == 1
    assert data["is_consistent"] is False

    mismatch = data["mismatches"][0]

    assert mismatch["book_title"] == "Atomic Habits"
    assert mismatch["expected_active_loans"] == 2
    assert mismatch["actual_active_loans"] == 0
    assert mismatch["difference"] == 2



def test_inventory_audit_includes_archived_books(client, db_session):
    # Arrange: create an archived book with inconsistent inventory
    book = Book(
        title="Python Crash Course",
        author="Eric Matthes",
        isbn="AUDIT-ARCHIVED-001",
        total_copies=3,
        available_copies=2,
        is_active=False
    )

    db_session.add(book)
    db_session.commit()

    # Act: request the inventory audit report
    response = client.get("/api/v1/reports/inventory-audit")

    # Assert: check the response
    assert response.status_code == 200

    data = response.json()

    assert data["total_books_checked"] == 1
    assert data["mismatched_books"] == 1
    assert data["is_consistent"] is False

    mismatch = data["mismatches"][0]

    assert mismatch["book_id"] == book.id
    assert mismatch["book_title"] == "Python Crash Course"
    assert mismatch["total_copies"] == 3
    assert mismatch["available_copies"] == 2

    assert mismatch["expected_active_loans"] == 1
    assert mismatch["actual_active_loans"] == 0
    assert mismatch["difference"] == 1


def test_most_borrowed_books_ranking(client, db_session):
    books = [
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="RANK-001",
            total_copies=5,
            available_copies=3,
            is_active=True
        ),
        Book(
            title="Atomic Habits",
            author="James Clear",
            isbn="RANK-002",
            total_copies=5,
            available_copies=4,
            is_active=True
        ),
        Book(
            title="Fluent Python",
            author="Luciano Ramalho",
            isbn="RANK-003",
            total_copies=5,
            available_copies=5,
            is_active=True
        )
    ]

    member = Member(
        full_name="Rahul Sharma",
        email="rahul.ranking@example.com",
        is_active=True
    )

    db_session.add_all(books + [member])
    db_session.commit()

    now = datetime.now(timezone.utc)

    # Clean Code: 3 borrowing transactions
    # Atomic Habits: 2 borrowing transactions
    # Fluent Python: 0 borrowing transactions

    loans = []

    for book, count in [
        (books[0], 3),
        (books[1], 2)
    ]:
        for i in range(count):
            is_active = i == 0

            loans.append(
                Loan(
                    book_id=book.id,
                    member_id=member.id,
                    borrowed_at=now - timedelta(days=20),
                    due_at=now - timedelta(days=6),
                    returned_at=(
                        None if is_active
                        else now - timedelta(days=5)
                    ),
                    status=(
                        "borrowed" if is_active
                        else "returned"
                    ),
                    renewal_count=0
                )
            )

    db_session.add_all(loans)
    db_session.commit()

    response = client.get(
        "/api/v1/reports/most-borrowed-books?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["title"] == "Clean Code"
    assert data[0]["borrow_count"] == 3

    assert data[1]["title"] == "Atomic Habits"
    assert data[1]["borrow_count"] == 2


def test_most_borrowed_books_limit(client, db_session):
    member = Member(
        full_name="Priya Sharma",
        email="priya.ranking@example.com",
        is_active=True
    )

    books = [
        Book(
            title=f"Book {i}",
            author="Test Author",
            isbn=f"RANK-LIMIT-{i}",
            total_copies=1,
            available_copies=0,
            is_active=True
        )
        for i in range(3)
    ]

    db_session.add_all([member] + books)
    db_session.commit()

    now = datetime.now(timezone.utc)

    for book in books:
        db_session.add(
            Loan(
                book_id=book.id,
                member_id=member.id,
                borrowed_at=now,
                due_at=now + timedelta(days=14),
                status="borrowed",
                renewal_count=0
            )
        )

    db_session.commit()

    response = client.get(
        "/api/v1/reports/most-borrowed-books?limit=2"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_most_borrowed_books_invalid_limit(client):
    response = client.get(
        "/api/v1/reports/most-borrowed-books?limit=0"
    )

    assert response.status_code == 422



def test_most_borrowed_includes_unborrowed_books(
    client,
    db_session
):
    books = [
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="UNBORROWED-001",
            total_copies=2,
            available_copies=2,
            is_active=True
        ),
        Book(
            title="Fluent Python",
            author="Luciano Ramalho",
            isbn="UNBORROWED-002",
            total_copies=1,
            available_copies=1,
            is_active=True
        )
    ]

    member = Member(
        full_name="Rahul Sharma",
        email="rahul.unborrowed@example.com",
        is_active=True
    )

    db_session.add_all(books + [member])
    db_session.commit()

    now = datetime.now(timezone.utc)

    loan = Loan(
        book_id=books[0].id,
        member_id=member.id,
        borrowed_at=now,
        due_at=now + timedelta(days=14),
        status="borrowed",
        renewal_count=0
    )

    # Keep inventory consistent with the active loan.
    books[0].available_copies = 1

    db_session.add(loan)
    db_session.commit()

    response = client.get(
        "/api/v1/reports/most-borrowed-books"
        "?include_unborrowed=true"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["title"] == "Clean Code"
    assert data[0]["borrow_count"] == 1

    assert data[1]["title"] == "Fluent Python"
    assert data[1]["borrow_count"] == 0

    response = client.get(
        "/api/v1/reports/most-borrowed-books"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Clean Code"
    #mistake check letter



def test_top_members_ranking(client, db_session):
    members = [
        Member(
            full_name="Rahul Sharma",
            email="rahul.top@example.com",
            is_active=True
        ),
        Member(
            full_name="Priya Patel",
            email="priya.top@example.com",
            is_active=True
        )
    ]

    book = Book(
        title="Test Analytics Book",
        author="Test Author",
        isbn="TOP-MEMBER-001",
        total_copies=5,
        available_copies=3,
        is_active=True
    )

    db_session.add_all(members + [book])
    db_session.commit()

    now = datetime.now(timezone.utc)

    loans = [
        # Rahul: 2 returned, 1 borrowed
        Loan(
            member_id=members[0].id,
            book_id=book.id,
            borrowed_at=now - timedelta(days=20),
            due_at=now - timedelta(days=6),
            returned_at=now - timedelta(days=5),
            status="returned",
            renewal_count=0
        ),
        Loan(
            member_id=members[0].id,
            book_id=book.id,
            borrowed_at=now - timedelta(days=18),
            due_at=now - timedelta(days=4),
            returned_at=now - timedelta(days=3),
            status="returned",
            renewal_count=0
        ),
        Loan(
            member_id=members[0].id,
            book_id=book.id,
            borrowed_at=now,
            due_at=now + timedelta(days=14),
            status="borrowed",
            renewal_count=0
        ),

        # Priya: 1 borrowed
        Loan(
            member_id=members[1].id,
            book_id=book.id,
            borrowed_at=now,
            due_at=now + timedelta(days=14),
            status="borrowed",
            renewal_count=0
        )
    ]

    db_session.add_all(loans)
    db_session.commit()

    response = client.get(
        "/api/v1/reports/top-members?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["full_name"] == "Rahul Sharma"
    assert data[0]["total_loans"] == 3
    assert data[0]["active_loans"] == 1
    assert data[0]["returned_loans"] == 2

    assert data[1]["full_name"] == "Priya Patel"
    assert data[1]["total_loans"] == 1
    assert data[1]["active_loans"] == 1
    assert data[1]["returned_loans"] == 0



def test_top_members_empty(client):
    response = client.get(
        "/api/v1/reports/top-members"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_loans_report(client, db_session):
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.overdue.report@example.com",
        is_active=True
    )

    books = [
        Book(
            title=f"Overdue Test Book {i}",
            author="Test Author",
            isbn=f"OVERDUE-REPORT-{i}",
            total_copies=2,
            available_copies=1,
            is_active=True
        )
        for i in range(3)
    ]

    db_session.add_all([member] + books)
    db_session.commit()

    now = datetime.now(timezone.utc)

    loans = [
        # Overdue by 18 days
        Loan(
            member_id=member.id,
            book_id=books[0].id,
            borrowed_at=now - timedelta(days=32),
            due_at=now - timedelta(days=18),
            status="borrowed",
            renewal_count=0
        ),

        # Active and not overdue
        Loan(
            member_id=member.id,
            book_id=books[1].id,
            borrowed_at=now,
            due_at=now + timedelta(days=14),
            status="borrowed",
            renewal_count=0
        ),

        # Returned, so excluded
        Loan(
            member_id=member.id,
            book_id=books[2].id,
            borrowed_at=now - timedelta(days=25),
            due_at=now - timedelta(days=11),
            returned_at=now - timedelta(days=9),
            status="returned",
            renewal_count=0
        )
    ]

    db_session.add_all(loans)
    db_session.commit()

    response = client.get("/api/v1/reports/overdue-loans")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    overdue = data[0]

    assert overdue["book_title"] == "Overdue Test Book 0"
    assert overdue["member_name"] == "Rahul Sharma"
    assert overdue["days_overdue"] == 18
    assert overdue["priority"] == "high"



def test_overdue_loans_min_days_filter(client, db_session):
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.min.overdue@example.com",
        is_active=True
    )

    books = [
        Book(
            title=f"Filter Test Book {i}",
            author="Test Author",
            isbn=f"OVERDUE-FILTER-{i}",
            total_copies=1,
            available_copies=0,
            is_active=True
        )
        for i in range(2)
    ]

    db_session.add_all([member] + books)
    db_session.commit()

    # Use midday UTC to keep calendar-day results stable.
    now = datetime.now(timezone.utc)

    loans = [
        Loan(
            member_id=member.id,
            book_id=books[0].id,
            borrowed_at=now - timedelta(days=24),
            due_at=now - timedelta(days=10),
            status="borrowed",
            renewal_count=0
        ),
        Loan(
            member_id=member.id,
            book_id=books[1].id,
            borrowed_at=now - timedelta(days=17),
            due_at=now - timedelta(days=3),
            status="borrowed",
            renewal_count=0
        )
    ]

    db_session.add_all(loans)
    db_session.commit()

    response = client.get(
        "/api/v1/reports/overdue-loans?min_days_overdue=7"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["book_title"] == "Filter Test Book 0"
    assert data[0]["days_overdue"] == 10
    assert data[0]["priority"] == "medium"


def test_overdue_loans_reject_negative_minimum(client):
    response = client.get(
        "/api/v1/reports/overdue-loans?min_days_overdue=-1"
    )

    assert response.status_code == 422