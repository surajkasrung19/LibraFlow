from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Loan(Base):
    __tablename__ = "loans"

    __table_args__ = (
        CheckConstraint(
            "status IN ('borrowed', 'returned')",
            name="ck_loans_status"
        ),
        CheckConstraint(
            "(status = 'borrowed' AND returned_at IS NULL) "
            "OR (status = 'returned' AND returned_at IS NOT NULL)",
            name="ck_loans_return_state"
        ),
        CheckConstraint(
            "due_at >= borrowed_at",
            name="ck_loans_due_date"
        ),
        Index("ix_loans_member_id", "member_id"),
        Index("ix_loans_book_id", "book_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id"),
        nullable=False
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        nullable=False
    )

    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        + timedelta(days=14),
        nullable=False
    )

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="borrowed",
        server_default="borrowed"
    )

    renewal_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0")