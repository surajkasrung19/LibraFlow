class DuplicateBookError(Exception):
    """Raised when a book with the given ISBN already exists"""

    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Book with ISBN {isbn} already exists")

class DuplicateMemberError(Exception):

    def __init__(self, email: str):
        self.email = email
        super().__init__(
            f"Member with email {email} already exists"
        )