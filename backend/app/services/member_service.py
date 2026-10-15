from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate
from app.services.exceptions import DuplicateMemberError


class MemberService:
    def __init__(self, db: Session):
        self.db = db

    def create_member(self, member_data: MemberCreate) -> Member:
        existing_member = self.get_member_by_email(
            str(member_data.email)
        )

        if existing_member is not None:
            raise DuplicateMemberError(str(member_data.email))

        member = Member(
            **member_data.model_dump()
        )

        self.db.add(member)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

            existing_member = self.get_member_by_email(
                str(member_data.email)
            )

            if existing_member is not None:
                raise DuplicateMemberError(
                    str(member_data.email)
                )

            raise 

        self.db.refresh(member)

        return member


    def get_member_by_email(self, email: str) -> Member | None:
        statement = select(Member).where(
            Member.email == email
        )

        return self.db.scalar(statement)


    def get_member_by_id(self, member_id: int) -> Member | None:
        return self.db.get(Member, member_id)


    def get_all_members(self) -> list[Member]:
        statement = (
            select(Member)
            .where(Member.is_active.is_(True))
            .order_by(Member.id)
        )

        return list(self.db.scalars(statement).all())

    def update_member(
        self,
        member_id: int,
        member_data: MemberUpdate
    ) -> Member | None:

        member = self.get_member_by_id(member_id)

        if member is None:
            return None

        changes = member_data.model_dump(exclude_unset=True)

        new_email = changes.get("email")

        if new_email is not None and new_email != member.email:
            existing = self.get_member_by_email(str(new_email))

            if existing is not None:
                raise DuplicateMemberError(str(new_email))

        for field, value in changes.items():
            setattr(member, field, value)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

            if new_email is not None:
                existing = self.get_member_by_email(str(new_email))

                if existing is not None and existing.id != member_id:
                    raise DuplicateMemberError(str(new_email))

            raise

        self.db.refresh(member)

        return member


    def deactivate_member(self, member_id: int) -> Member | None:
        member = self.get_member_by_id(member_id)

        if member is None:
            return None

        if not member.is_active:
            return member

        member.is_active = False

        self.db.commit()
        self.db.refresh(member)

        return member