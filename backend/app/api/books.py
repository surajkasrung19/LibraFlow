from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.db.session import get_db
from app.schemas.book import BookCreate, BookResponse
from app.services.book_service import BookService
from app.services.exceptions import DuplicateBookError

router = APIRouter(
    prefix="/api/v1/books",
    tags=["Books"]
)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db)
):
    service = BookService(db)

    existing_book = service.get_book_by_isbn(book_data.isbn)

    if existing_book is not None: 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A book with this ISBN already exists"
        )

    try:
        return service.create_book(book_data)

    except DuplicateBookError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A book with this ISBN already exists"
        )from None

    

@router.get(
    "",
    response_model=list[BookResponse]
)
def get_books(db: Session = Depends(get_db)):
    service = BookService(db)

    return service.get_all_books()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    service = BookService(db)

    book = service.get_book_by_id(book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book

