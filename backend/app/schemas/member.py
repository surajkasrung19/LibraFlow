from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class MemberBase(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value):
        if not isinstance(value, str):
            raise ValueError("Full name must be a string")

        return normalize_full_name(value)

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_member_name(cls, value):
        if isinstance(value, str):
            return value.strip()

        return value


    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return normalize_email(value)


    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        return normalize_phone(value)


def normalize_full_name(value: str) -> str:
    name = " ".join(value.split())

    if len(name) < 2:
        raise ValueError(
            "Full name must contain at least 2 characters"
        )

    return name


def normalize_email(value: str) -> str:
    return str(value).lower()


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None

    phone = value.strip().replace(" ", "")

    if not phone:
        return None

    digits = phone[1:] if phone.startswith("+") else phone

    if not digits.isdigit():
        raise ValueError("Phone number must contain only digits")

    if not 7 <= len(digits) <= 15:
        raise ValueError("Phone number must contain 7 to 15 digits")

    return phone



class MemberCreate(MemberBase):
    pass


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    joined_at: datetime
    is_active: bool


class MemberUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value):
        if value is None:
            raise ValueError("Full name cannot be null")

        if not isinstance(value, str):
            raise ValueError("Full name must be a string")

        return normalize_full_name(value)

    @field_validator("email", mode="after")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            raise ValueError("Email cannot be null")

        return normalize_email(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        return normalize_phone(value)