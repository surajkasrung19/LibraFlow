from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.member import (
    MemberCreate,
    MemberResponse,
    MemberUpdate,
)
from app.services.member_service import MemberService
from app.services.exceptions import DuplicateMemberError


router = APIRouter(
    prefix="/api/v1/members",
    tags=["Members"]
)


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED
)
def register_member(
    member_data: MemberCreate,
    db: Session = Depends(get_db)
):
    service = MemberService(db)

    try:
        return service.create_member(member_data)

    except DuplicateMemberError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc


@router.get(
    "",
    response_model=list[MemberResponse]
)
def list_members(db: Session = Depends(get_db)):
    service = MemberService(db)

    return service.get_all_members()


@router.get(
    "/{member_id}",
    response_model=MemberResponse
)
def get_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    service = MemberService(db)

    member = service.get_member_by_id(member_id)

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member


@router.patch(
    "/{member_id}",
    response_model=MemberResponse
)
def update_member(
    member_id: int,
    member_data: MemberUpdate,
    db: Session = Depends(get_db)
):
    service = MemberService(db)

    try:
        member = service.update_member(member_id, member_data)

    except DuplicateMemberError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member


@router.patch(
    "/{member_id}/deactivate",
    response_model=MemberResponse
)
def deactivate_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    service = MemberService(db)

    member = service.deactivate_member(member_id)

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member