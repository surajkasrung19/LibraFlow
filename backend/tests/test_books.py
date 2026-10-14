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


def test_update_book(client):

   response = client.post(
       "/api/v1/books",
       json={
           "title": "Original Title",
           "author": "Original AUthor",
           "isbn": "9780132350999",
           "total_copies": 2
       }
   )

   assert response.status_code == 201

   book_id = response.json()["id"]

   #Step 2: update only the title
   update_response = client.patch(
       f"/api/v1/books/{book_id}",
       json={"title": "Updated Title"}
   )

   assert update_response.status_code == 200

   data = update_response.json()

   #step 3 Verify the update
   assert data["title"] == "Updated Title"
   assert data["author"] == "Original AUthor"
   assert data["total_copies"] == 2

   #Step 4: Verify the database persisted the change
   get_response = client.get(
       f"/api/v1/books/{book_id}"
   )

   assert get_response.status_code == 200
   assert get_response.json()["title"] == "Updated Title"


def test_update_nonexistent_book(client):

    response = client.patch(
        "/api/v1/books/99999",
        json={"title": "Updated Title"}
    )

    assert response.status_code == 404
    
    data = response.json()

    assert data["detail"] == "Book not found"



def test_archive_book(client):
    # Create a book
    response = client.post(
        "/api/v1/books",
        json={
            "title": "Effective Python",
            "author": "Brett Slatkin",
            "isbn": "9780134853987",
            "category": "Programming",
            "total_copies": 3
        }
    )

    assert response.status_code == 201

    book_id = response.json()["id"]

    # Archive the book
    archive_response = client.patch(
        f"/api/v1/books/{book_id}/archive"
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["is_active"] is False

    # Confirm it's absent from the active catalogue
    list_response = client.get("/api/v1/books")

    assert list_response.status_code == 200

    book_ids = [
        book["id"]
        for book in list_response.json()
    ]

    assert book_id not in book_ids

    # Confirm the archived record still exists
    detail_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert detail_response.status_code == 200
    assert detail_response.json()["is_active"] is False


def test_archive_already_archived_book(client):
    # 1. Create a book
    response = client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "9780132350884",
            "total_copies": 2
        }
    )

    assert response.status_code == 201

    book_id = response.json()["id"]

    # 2. Archive the book for the first time
    first_archive = client.patch(
        f"/api/v1/books/{book_id}/archive"
    )

    assert first_archive.status_code == 200
    assert first_archive.json()["is_active"] is False

    # 3. Archive the same book again
    second_archive = client.patch(
        f"/api/v1/books/{book_id}/archive"
    )

    assert second_archive.status_code == 200
    assert second_archive.json()["is_active"] is False

    # 4. Verify the stored state
    get_response = client.get(
        f"/api/v1/books/{book_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_archive_nonexistent_book(client):
    response = client.patch(
        "/api/v1/books/99999/archive"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Book not found"






