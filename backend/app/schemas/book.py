from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    isbn: str = Field(min_length=10, max_length=20)
    category: str | None = Field(default=None, max_length=100)
    total_copies: int = Field(gt=0)

    @field_validator(
        "title",
        "author",
        "isbn",
        mode="before"
    )
    @classmethod
    def striopo_required_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int
    created_at: datetime
    is_active: bool

class BookUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    author: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    category: str | None = Field(
        default=None,
        max_length=100
    )


