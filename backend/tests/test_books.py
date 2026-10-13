def test_create_book_success(client):
    payload = {
        "title": "Atomic Habits",
        "author": "James Clear",
        "isbn": "9780735211292",
        "category": "Self Development",
        "total_copies" : 5
    }

    response = client.post(
        "/api/v1/books",
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Atomic Habits"
    assert data["available_copies"] == 5
    assert data["id"] > 0

def test_duplicate_isbn_returns_409(client):
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "category": "Programming",
        "total_copies": 3
    }

    first_response = client.post(
        "/api/v1/books",
        json=payload
    )

    second_response = client.post(
        "/api/v1/books",
        json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "A book with this ISBN already exists"
    )


def test_negative_total_copies(client):
    payload = {
        "title": "Grokking Algorithm",
        "author": "Aditya Bhargava",
        "isbn": "9780132350888",
        "category": "Programming",
        "total_copies": -5    
    }

    response = client.post(
        "/api/v1/books",
        json=payload
    )

    assert response.status_code == 422

    data = response.json()
    assert "detail" in data

def test_get_missing_book(client):

    response = client.get(
        "/api/v1/books/99999",
    )

    assert response.status_code == 404

    data = response.json()
    
    assert data["detail"] == "Book not found"
