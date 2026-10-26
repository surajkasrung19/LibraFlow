from app.core.config import settings
from app.models.book import Book
from app.models.member import Member

def test_renew_missing_loan_returns_404(client):
    response = client.patch(
        "/api/v1/loans/9999/renew"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Loan not found"
    }


def test_renew_returend_loan_returene_409(client, db_session):
    member = Member(
        full_name="Rahul Sharma",
        email="rahul.exception@example.com",
        is_active=True
    )

    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="EXCEPTION-TEST-001",
        total_copies=1,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    borrow_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": member.id,
            "book_id": book.id
        }
    )

    assert borrow_response.status_code == 201

    loan_id = borrow_response.json()["id"]

    return_response = client.patch(
        f"/api/v1/loans/{loan_id}/return"
    )

    assert return_response.status_code == 200

    renew_response = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert renew_response.status_code == 409

    assert renew_response.json() == {
        "detail": "Only borrowed loans can be renewed"
    }


def test_renewal_limit_returns_409(client, db_session, monkeypatch):

    monkeypatch.setattr(settings, "max_loan_renewals", 1)

    member = Member(
        full_name="Rahul Sharma",
        email="rahul.limit@example.com",
        is_active=True
    )

    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="EXCEPTION-RENEW-LIMIT-001",
        total_copies=2,
        available_copies=2,
        is_active=True
    )

    db_session.add_all([member, book])
    db_session.commit()

    borrow_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": member.id,
            "book_id": book.id
        }
    )

    assert borrow_response.status_code == 201

    loan_id = borrow_response.json()["id"]

    first_response = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert first_response.status_code == 200
    assert first_response.json()["renewal_count"] == 1

    due_date_after_first_renewal = (
        first_response.json()["due_at"]
    )

    second_response = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "Loan renewal limit reached"
    }

    # ASSERT: Verify that the rejected request
    # did not modify the loan.
    saved_response = client.get(
        f"/api/v1/loans/{loan_id}"
    )

    assert saved_response.status_code == 200

    saved_loan = saved_response.json()

    assert saved_loan["renewal_count"] == 1
    assert saved_loan["due_at"] == due_date_after_first_renewal

    # Renewal must not change book inventory
    db_session.refresh(book)
    assert book.available_copies == 1