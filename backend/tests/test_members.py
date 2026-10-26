def test_register_member(client):
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "RAHUL@EXAMPLE.COM",
            "phone": "+919876543210"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Rahul Sharma"
    assert data["email"] == "rahul@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_duplicate_member_email(client):
    # Arrange: Register the first member
    first = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul@example.com"
        }
    )

    assert first.status_code == 201

    # Act: Register another member with the same email
    second = client.post(
        "/api/v1/members",
        json={
            "full_name": "Another Rahul",
            "email": "RAHUL@EXAMPLE.COM"
        }
    )

    # Assert: Duplicate registration must fail
    assert second.status_code == 409

    data = second.json()

    assert "already exists" in data["detail"]

def test_update_member(client):
    # Arrange: Register a member
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Priya Sharma",
            "email": "priya@example.com",
            "phone": "9876543210"
        }
    )

    assert response.status_code == 201

    member_id = response.json()["id"]

    # Act: Update only the phone number
    update_response = client.patch(
        f"/api/v1/members/{member_id}",
        json={
            "phone": "+919999999999"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    # Assert: Phone changed
    assert data["phone"] == "+919999999999"

    # Assert: Other information remains unchanged
    assert data["full_name"] == "Priya Sharma"
    assert data["email"] == "priya@example.com"

    # Verify that the update was persisted
    get_response = client.get(
        f"/api/v1/members/{member_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["phone"] == "+919999999999"


def test_deactivate_member(client):
    # Arrange: Register a member
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Amit Patel",
            "email": "amit@example.com"
        }
    )

    assert response.status_code == 201

    member_id = response.json()["id"]

    # Act: Deactivate the member
    deactivate_response = client.patch(
        f"/api/v1/members/{member_id}/deactivate"
    )

    assert deactivate_response.status_code == 200

    data = deactivate_response.json()

    assert data["is_active"] is False

    # Assert: Member no longer appears in active list
    list_response = client.get("/api/v1/members")

    assert list_response.status_code == 200

    active_member_ids = [
        member["id"]
        for member in list_response.json()
    ]

    assert member_id not in active_member_ids

    # Assert: Member is still stored
    get_response = client.get(
        f"/api/v1/members/{member_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_deactivate_member_twice(client):
    # Step 1: Register a member
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "rahul@example.com"
        }
    )

    assert response.status_code == 201

    member_id = response.json()["id"]

    # Step 2: Deactivate for the first time
    first_response = client.patch(
        f"/api/v1/members/{member_id}/deactivate"
    )

    assert first_response.status_code == 200
    assert first_response.json()["is_active"] is False

    # Step 3: Deactivate for the second time
    second_response = client.patch(
        f"/api/v1/members/{member_id}/deactivate"
    )

    assert second_response.status_code == 200
    assert second_response.json()["is_active"] is False

    # Step 4: Verify the member's final state
    get_response = client.get(
        f"/api/v1/members/{member_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_register_member_invalid_email(client):
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Rahul Sharma",
            "email": "invalid-email",
            "phone": "9876543210"
        }
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data


def test_get_nonexistent_member(client):
    response = client.get("/api/v1/members/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


def test_update_member_null_name(client):
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "Priya Sharma",
            "email": "priya@example.com"
        }
    )

    assert response.status_code == 201

    member_id = response.json()["id"]

    update_response = client.patch(
        f"/api/v1/members/{member_id}",
        json={"full_name": None}
    )

    assert update_response.status_code == 422

def test_register_member_rejects_blank_name(client):
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "   ",
            "email": "blank.member@example.com"
        }
    )

    assert response.status_code == 422


def test_register_member_strips_name_whitespace(client):
    response = client.post(
        "/api/v1/members",
        json={
            "full_name": "  Rahul Sharma  ",
            "email": "rahul.validation@example.com"
        }
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == "Rahul Sharma"
