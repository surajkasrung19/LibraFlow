from pydantic import BaseModel, Field
from datetime import datetime

class LibraryOverviewResponse(BaseModel):
    total_book_titles: int = Field(ge=0)
    total_book_copies: int = Field(ge=0)
    available_book_copies: int = Field(ge=0)
    borrowed_book_copies: int = Field(ge=0)
    active_members: int = Field(ge=0)
    active_loans: int = Field(ge=0)
    returned_loans: int = Field(ge=0)
    overdue_loans: int = Field(ge=0)

class InventoryMismatchResponse(BaseModel):
    book_id: int
    book_title: str
    total_copies: int
    available_copies: int
    expected_active_loans: int
    actual_active_loans: int
    difference: int


class InventoryAuditResponse(BaseModel):
    total_books_checked: int
    mismatched_books: int
    is_consistent: bool
    mismatches: list[InventoryMismatchResponse]

class MostBorrowedBookResponse(BaseModel):
    book_id: int
    title: str
    author: str
    borrow_count: int = Field(ge=0)


class TopMemberResponse(BaseModel):
    member_id: int
    full_name: str
    total_loans: int = Field(ge=0)
    active_loans: int = Field(ge=0)
    returned_loans: int = Field(ge=0)


class OverdueLoanResponse(BaseModel):
    loan_id: int
    book_id: int
    book_title: str
    member_id: int
    member_name: str
    borrowed_at: datetime
    due_at: datetime
    days_overdue: int = Field(ge=0)
    priority: str