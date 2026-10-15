from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Member(Base):
    __tablename__ = "members"

    __table_args__ = (
        UniqueConstraint(
            "email",
            name="uq_members_email"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False
    )