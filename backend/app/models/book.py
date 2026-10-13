from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Book(Base):
    __tablename__ = "books"

    __table_args__ = (
        UniqueConstraint("isbn", name="uq_books_isbn"),
        CheckConstraint(
            "total_copies >= 0",
            name="ck_books_total_nonnegative"
        ),
        CheckConstraint(
            "available_copies >= 0 "
            "AND available_copies <= total_copies",
            name="ck_books_available_range"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    author: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    isbn: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    total_copies: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    available_copies: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )