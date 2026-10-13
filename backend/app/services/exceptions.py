class DuplicateBookError(Exception):
    """Raised when a book with the given ISBN already exists"""

    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Book with ISBN {isbn} already exists")

        