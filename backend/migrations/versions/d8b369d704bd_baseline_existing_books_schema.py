"""baseline existing books schema

Revision ID: d8b369d704bd
Revises: 
Create Date: 2026-10-13 20:16:18.922739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8b369d704bd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("author", sa.String(150), nullable=False),
        sa.Column("isbn", sa.String(20), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("total_copies", sa.Integer(), nullable=False),
        sa.Column("available_copies", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),

        sa.UniqueConstraint(
            "isbn", 
            name="uq_books_isbn"
        ),

        sa.CheckConstraint(
            "total_copies >= 0",
            name="ck_books_total_copies"
        ),

        sa.CheckConstraint(
            "available_copies >= 0 AND available_copies <= total_copies",
            name="ck_books_available_copies"
        )
    )


def downgrade() -> None:
    op.drop_table("books")
