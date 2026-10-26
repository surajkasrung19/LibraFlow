from app.core.config import settings

def test_complete_borrowing_lifecycle(client):
    # STEP 1: Register a book
    book_response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "INT-LIFECYCLE-001",
            "total_copies": 2
        }
    )

    assert book_response.status_code == 201

    book_id = book_response.json()["id"]

    # STEP 2: Register a member
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul.lifecycle@example.com"
        }
    )

    assert member_response.status_code == 201

    member_id = member_response.json()["id"]

    # STEP 3: Borrow the book
    borrow_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": member_id,
            "book_id": book_id
        }
    )

    assert borrow_response.status_code == 201

    loan_id = borrow_response.json()["id"]

    # STEP 4: Verify inventory decreased
    book_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert book_response.status_code == 200
    assert book_response.json()["available_copies"] == 1

    # STEP 5: Renew the loan
    renew_response = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert renew_response.status_code == 200
    assert renew_response.json()["renewal_count"] == 1

    # Renewal must not change inventory.
    book_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert book_response.json()["available_copies"] == 1

    # STEP 6: Return the book
    return_response = client.patch(
        f"/api/v1/loans/{loan_id}/return"
    )

    assert return_response.status_code == 200
    assert return_response.json()["status"] == "returned"

    # STEP 7: Verify inventory restored
    book_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert book_response.json()["available_copies"] == 2

    # STEP 8: Verify Library Overview analytics
    report_response = client.get(
        "/api/v1/reports/overview"
    )

    assert report_response.status_code == 200

    report = report_response.json()

    assert report["total_book_titles"] == 1
    assert report["total_book_copies"] == 2
    assert report["available_book_copies"] == 2
    assert report["borrowed_book_copies"] == 0
    assert report["active_loans"] == 0
    assert report["returned_loans"] == 1

    # STEP 9: Verify inventory audit
    audit_response = client.get(
        "/api/v1/reports/inventory-audit"
    )

    assert audit_response.status_code == 200

    audit = audit_response.json()

    assert audit["is_consistent"] is True
    assert audit["mismatched_books"] == 0


def test_double_renewal_preserves_loan_state(client, monkeypatch):
    # ARRANGE: Allow exactly one renewal.
    monkeypatch.setattr(settings, "max_loan_renewals", 1)

    # Step 1: Create a book.
    book_response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "WORKFLOW-RENEW-001",
            "total_copies": 2
        }
    )

    assert book_response.status_code == 201
    book_id = book_response.json()["id"]

    # Step 2: Register a member.
    member_response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul.double.renew@example.com"
        }
    )

    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    # Step 3: Borrow the book.
    borrow_response = client.post(
        "/api/v1/loans",
        json={
            "member_id": member_id,
            "book_id": book_id
        }
    )

    assert borrow_response.status_code == 201
    loan_id = borrow_response.json()["id"]

    # Step 4: First renewal succeeds.
    first_renewal = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert first_renewal.status_code == 200

    first_data = first_renewal.json()

    assert first_data["renewal_count"] == 1

    # Save the persisted values for comparison.
    due_date_after_first_renewal = first_data["due_at"]

    # Capture analytics before attempting the invalid renewal
    overview_before_response = client.get(
        "/api/v1/reports/overview"
    )

    assert overview_before_response.status_code == 200

    overview_before = overview_before_response.json()

    audit_before_response = client.get(
        "/api/v1/reports/inventory-audit"
    )

    assert audit_before_response.status_code == 200

    audit_before = audit_before_response.json()


    # Verify the expected state after one successful renewal
    assert overview_before["active_loans"] == 1
    assert overview_before["returned_loans"] == 0
    assert overview_before["borrowed_book_copies"] == 1
    assert overview_before["available_book_copies"] == 1

    assert audit_before["is_consistent"] is True
    assert audit_before["mismatched_books"] == 0

    # Step 5: Second renewal must fail.
    second_renewal = client.patch(
        f"/api/v1/loans/{loan_id}/renew"
    )

    assert second_renewal.status_code == 409

    assert second_renewal.json() == {
        "detail": "Loan renewal limit reached"
    }

    # Step 6: Retrieve the saved loan from the API.
    saved_response = client.get(
        f"/api/v1/loans/{loan_id}"
    )

    assert saved_response.status_code == 200

    saved_loan = saved_response.json()

    # ASSERT: Failed renewal did not modify loan data.
    assert saved_loan["renewal_count"] == 1

    assert (
        saved_loan["due_at"]
        == due_date_after_first_renewal
    )

    assert saved_loan["status"] == "borrowed"
    assert saved_loan["returned_at"] is None

    # Step 7: Verify book inventory also remains correct.
    book_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert book_response.status_code == 200

    saved_book = book_response.json()

    assert saved_book["total_copies"] == 2
    assert saved_book["available_copies"] == 1

    # Bonus Verify analytics after the rejected renewal
    overview_after_response = client.get(
        "/api/v1/reports/overview"
    )

    assert overview_after_response.status_code == 200

    overview_after = overview_after_response.json()

    # Failed renewal must not alter circlualation statistics
    assert overview_after == overview_before

    # Verify nventory audit after the failed operation
    audit_after_response = client.get(
        "/api/v1/reports/inventory-audit"
    )

    assert audit_after_response.status_code == 200

    audit_after = audit_after_response.json()

    assert audit_after == audit_before
    assert audit_after["is_consistent"] is True
    assert audit_after["mismatched_books"] == 0