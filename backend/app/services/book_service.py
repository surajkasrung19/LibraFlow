from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.exceptions import DuplicateBookError
from app.models.book import Book
from app.schemas.book import BookCreate

class BookService:

    def __init__(self, db: Session):
        self.db = db

    def create_book(self, book_data: BookCreate) -> Book:
        book = Book(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn,
            category=book_data.category,
            total_copies=book_data.total_copies,
            available_copies=book_data.total_copies
        )


        try:
            self.db.add(book)
            self.db.commit()
            self.db.refresh(book)

            return book

        except IntegrityError as exc:
            self.db.rollback()

            existing_book = self.get_book_by_isbn(book_data.isbn)

            if existing_book is not None:
                raise DuplicateBookError(book_data.isbn) from exc

            raise
        

    def get_all_books(self) -> list[Book]:
        statement = select(Book).order_by(Book.id)

        return list(
            self.db.scalars(statement).all()
        )

    def get_book_by_id(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)


    def get_book_by_isbn(self, isbn: str) -> Book | None:
        statement = select(Book).where(Book.isbn == isbn)

        return self.db.scalar(statement)
    