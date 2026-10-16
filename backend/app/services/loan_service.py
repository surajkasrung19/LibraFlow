from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan
from app.schemas.loan import LoanCreate
from app.services.exceptions import LoanError


class LoanService:
    def __init__(self, db: Session):
        self.db = db

    def create_loan(self, loan_data: LoanCreate) -> Loan:
        member = self.db.get(Member, loan_data.member_id)

        if member is None:
            raise LoanError("Member not found")

        if not member.is_active:
            raise LoanError("Member is inactive")

        book = self.db.get(Book, loan_data.book_id)

        if book is None:
            raise LoanError("Book not found")

        if not book.is_active:
            raise LoanError("Book is archived")

        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=14)

        try:
            #Reduce inventory only when a copy is available
            statement = (
                update(Book)
                .where(
                    Book.id == loan_data.book_id,
                    Book.is_active.is_(True),
                    Book.available_copies > 0
                )
                .values(
                    available_copies=Book.available_copies -1
                )
                .execution_options(synchronize_session=False)
            )

            result = self.db.execute(statement)

            if result.rowcount != 1:
                raise LoanError("No available copies")

            #Create the borrowing record

            loan = Loan(
                member_id=loan_data.member_id,
                book_id=loan_data.book_id,
                borrowed_at=now,
                due_at=due_date,
                returned_at=None,
                status="borrowed"
            )

            self.db.add(loan)

            #Persist inventory and Loan together
            self.db.commit()

            self.db.refresh(loan)

            return loan

        except Exception:
            self.db.rollback()
            raise


    def return_loan(self, loan_id: int) -> Loan:
    # 1. Find the loan
        loan = self.db.get(Loan, loan_id)

        if loan is None:
            raise LoanError("Loan not found")

        # 2. Prevent double returns
        if loan.status == "returned":
            return loan

        try:
        # 3. Claim this loan for return, only if still borrowed
            result = self.db.execute(
                update(Loan)
                .where(
                    Loan.id == loan_id,
                    Loan.status == "borrowed"
                )
                .values(
                    status="returned",
                    returned_at=datetime.now(timezone.utc)
                )
                .execution_options(synchronize_session=False)
            )

            if result.rowcount != 1:
                raise LoanError("Loan is no longer available for return")

            # 4. Restore one available copy
            inventory_result = self.db.execute(
                update(Book)
                .where(
                    Book.id == loan.book_id,
                    Book.available_copies < Book.total_copies
                )
                .values(
                    available_copies=Book.available_copies + 1
                )
                .execution_options(synchronize_session=False)
            )

            if inventory_result.rowcount != 1:
                raise LoanError("Unable to restore book inventory")

            # 5. Save both changes together
            self.db.commit()

            # 6. Reload the updated loan
            self.db.expire_all()
            updated_loan = self.db.get(Loan, loan_id)

            return updated_loan

        except Exception:
            self.db.rollback()
            raise


    def get_loan_by_id(self, loan_id: int) -> Loan | None:
        return self.db.get(Loan, loan_id)


    def get_all_loans(self, active_only: bool = False) -> list[Loan]:
        statement = select(Loan)

        if active_only:
            statement = statement.where(Loan.status == "borrowed")

        statement = statement.order_by(Loan.id.desc())

        return list(self.db.scalars(statement).all())


    def get_member_loans(self, member_id: int) -> list[Loan]:
        statement = (
            select(Loan)
            .where(Loan.member_id == member_id)
            .order_by(Loan.id.desc())
        )

        return list(self.db.scalars(statement).all())
