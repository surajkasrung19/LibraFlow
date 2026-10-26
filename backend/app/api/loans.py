from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.loan import LoanCreate, LoanResponse
from app.services.loan_service import LoanService
from app.services.exceptions import LoanError


router = APIRouter(
    prefix="/api/v1/loans",
    tags=["Loans"]
)


#Borrow Book Endpoint
@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED
)
def borrow_book(
    loan_data: LoanCreate,
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    try:
        return service.create_loan(loan_data)

    except LoanError as exc:
        message = str(exc)

        if message in ("Member not found", "Book not found"):
            error_status = status.HTTP_404_NOT_FOUND
        else:
            error_status = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=error_status,
            detail=message
        ) from exc

#return book endpoint
@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse
)
def return_book(
    loan_id: int,
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    try:
        return service.return_loan(loan_id)

    except LoanError as exc:
        message = str(exc)

        error_status = (
            status.HTTP_404_NOT_FOUND
            if message == "Loan not found"
            else status.HTTP_409_CONFLICT
        )

        raise HTTPException(
            status_code=error_status,
            detail=message
        ) from exc


#List all loans
@router.get(
    "",
    response_model=list[LoanResponse]
)
def list_loans(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    return service.get_all_loans(active_only=active_only)


#relative member borrowing history
@router.get(
    "/member/{member_id}",
    response_model=list[LoanResponse]
)
def get_member_loan_history(
    member_id: int,
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    return service.get_member_loans(member_id)


#Retrieve a single loan
@router.get(
    "/{loan_id}",
    response_model=LoanResponse
)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    loan = service.get_loan_by_id(loan_id)

    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )

    return loan


@router.patch(
    "/{loan_id}/renew",
    response_model=LoanResponse
)
def renew_book_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
    service = LoanService(db)

    return service.renew_loan(loan_id)