from datetime import datetime

from pydantic  import BaseModel, Field, ConfigDict

class LoanCreate(BaseModel):
    member_id: int = Field(gt=0)
    book_id: int = Field(gt=0)

class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    book_id: int

    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None

    status: str
