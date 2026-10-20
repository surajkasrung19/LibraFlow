from datetime import datetime, timezone

from sqlalchemy import func, select, case
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan

from app.schemas.report import (
    LibraryOverviewResponse,
    InventoryMismatchResponse,
    InventoryAuditResponse,
    MostBorrowedBookResponse,
    TopMemberResponse,
    OverdueLoanResponse
)

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    #Count book titles
    def get_library_overview(self) -> LibraryOverviewResponse:
        total_book_titles = self.db.scalar(
            select(func.count(Book.id))
            .where(Book.is_active.is_(True))
        ) or 0

        total_book_copies = self.db.scalar(
            select(func.coalesce(func.sum(Book.total_copies), 0))
            .where(Book.is_active.is_(True))
        ) or 0

        available_book_copies = self.db.scalar(
            select(func.coalesce(
                func.sum(Book.available_copies),
                0
            )).where(Book.is_active.is_(True))
        ) or 0

        active_members =self.db.scalar(
            select(func.count(Member.id))
            .where(Member.is_active.is_(True))
        ) or 0

        active_loans = self.db.scalar(
            select(func.count(Loan.id))
            .where(Loan.status == "borrowed")
        ) or 0

        returned_loans = self.db.scalar(
            select(func.count(Loan.id))
            .where(Loan.status == "returned")
        ) or 0

        now = datetime.now(timezone.utc)

        overdue_loans = self.db.scalar(
            select(func.count(Loan.id))
            .where(
                Loan.status == "borrowed",
                Loan.due_at < now
            )
        ) or 0

        return LibraryOverviewResponse(
            total_book_titles=total_book_titles,
            total_book_copies=total_book_copies,
            available_book_copies=available_book_copies,
            borrowed_book_copies = active_loans,
            active_members=active_members,
            active_loans=active_loans,
            returned_loans=returned_loans,
            overdue_loans=overdue_loans
        )

    def get_inventory_audit(self) -> InventoryAuditResponse:
        active_loan_counts = (
            select(
                Loan.book_id.label("book_id"),
                func.count(Loan.id).label("active_loans")
            )
            .where(Loan.status == "borrowed")
            .group_by(Loan.book_id)
            .subquery()
        )

        statement = (
            select(
                Book.id,
                Book.title,
                Book.total_copies,
                Book.available_copies,
                func.coalesce(
                    active_loan_counts.c.active_loans, 0
                ).label("actual_active_loans")
            )
            .outerjoin(
                active_loan_counts,
                Book.id == active_loan_counts.c.book_id
            )
            .order_by(Book.id)
        )

        rows = self.db.execute(statement).all()

        mismatches = []

        for row in rows:
            expected = row.total_copies - row.available_copies
            actual = row.actual_active_loans

            if expected != actual:
                mismatches.append(
                    InventoryMismatchResponse(
                        book_id=row.id,
                        book_title=row.title,
                        total_copies=row.total_copies,
                        available_copies=row.available_copies,
                        expected_active_loans=expected,
                        actual_active_loans=actual,
                        difference=expected - actual
                    )
                )

        return InventoryAuditResponse(
            total_books_checked=len(rows),
            mismatched_books=len(mismatches),
            is_consistent=len(mismatches) == 0,
            mismatches=mismatches
        )


    def get_most_borrowed_books(
        self,
        limit: int = 5,
        include_unborrowed: bool = False
    ) -> list[MostBorrowedBookResponse]:

        statement = select(
            Book.id.label("book_id"),
            Book.title,
            Book.author,
            func.count(Loan.id).label("borrow_count")
        )

        if include_unborrowed:
            # LEFT OUTER JOIN includes books with zero loans.
            statement = statement.outerjoin(
                Loan,
                Loan.book_id == Book.id
            )
        else:
            # INNER JOIN includes only borrowed books.
            statement = statement.join(
                Loan,
                Loan.book_id == Book.id
            )

        statement = (
            statement
            .group_by(Book.id, Book.title, Book.author)
            .order_by(
                func.count(Loan.id).desc(),
                Book.id.asc()
            )
            .limit(limit)
        )

        rows = self.db.execute(statement).all()
        print("include_unborrowed:", include_unborrowed)
        print("Generated SQL:", statement)

        return [
            MostBorrowedBookResponse(
                book_id=row.book_id,
                title=row.title,
                author=row.author,
                borrow_count=row.borrow_count
            )
            for row in rows
        ]

    def get_top_members(
        self,
        limit: int = 5
    ) -> list[TopMemberResponse]:

        statement = (
            select(
                Member.id.label("member_id"),
                Member.full_name,
                func.count(Loan.id).label("total_loans"),

                func.sum(
                    case(
                        (Loan.status == "borrowed", 1),
                        else_=0
                    )
                ).label("active_loans"),

                func.sum(
                    case(
                        (Loan.status == "returned", 1),
                        else_=0
                    )
                ).label("returned_loans")
            )
            .join(Loan, Loan.member_id == Member.id)
            .group_by(
                Member.id,
                Member.full_name
            )
            .order_by(
                func.count(Loan.id).desc(),
                Member.id.asc()
            )
            .limit(limit)
        )

        rows = self.db.execute(statement).all()


        return [
            TopMemberResponse(
                member_id=row.member_id,
                full_name=row.full_name,
                total_loans=row.total_loans,
                active_loans=row.active_loans,
                returned_loans=row.returned_loans
            )
            for row in rows
        ]


    def get_overdue_loans(
        self,
        min_days_overdue: int = 0
    ) -> list[OverdueLoanResponse]:
        now = datetime.now(timezone.utc)

        statement = (
            select(
                Loan.id.label("loan_id"),
                Loan.book_id,
                Book.title.label("book_title"),
                Loan.member_id,
                Member.full_name.label("member_name"),
                Loan.borrowed_at,
                Loan.due_at
            )
            .join(Book, Book.id == Loan.book_id)
            .join(Member, Member.id == Loan.member_id)
            .where(
                Loan.status == "borrowed",
                Loan.due_at < now
            )
            .order_by(Loan.due_at.asc(), Loan.id.asc())
        )

        rows = self.db.execute(statement).all()

        results = []

        for row in rows:
            due_at = row.due_at

            # SQLite may return naive datetime values.
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=timezone.utc)

            days_overdue = (now.date() - due_at.date()).days

             # Skip loans below the requested threshold.
            if days_overdue < min_days_overdue:
                continue

            if days_overdue >= 15:
                priority = "high"
            elif days_overdue >= 6:
                priority = "medium"
            else:
                priority = "low"

            results.append(
                OverdueLoanResponse(
                    loan_id=row.loan_id,
                    book_id=row.book_id,
                    book_title=row.book_title,
                    member_id=row.member_id,
                    member_name=row.member_name,
                    borrowed_at=row.borrowed_at,
                    due_at=due_at,
                    days_overdue=days_overdue,
                    priority=priority
                )
            )

        return results