from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import(
    LibraryOverviewResponse,
    InventoryAuditResponse,
    MostBorrowedBookResponse,
    TopMemberResponse,
    OverdueLoanResponse
)
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@router.get(
    "/overview",
    response_model=LibraryOverviewResponse
)
def get_library_overview(
    db: Session = Depends(get_db)
):
    service = ReportService(db)
    return service.get_library_overview()

@router.get(
    "/inventory-audit",
    response_model=InventoryAuditResponse
)
def get_inventory_audit(
    db: Session = Depends(get_db)
):
    service = ReportService(db)
    return service.get_inventory_audit()


@router.get(
    "/most-borrowed-books",
    response_model=list[MostBorrowedBookResponse]
)
def get_most_borrowed_books(
    limit: int = Query(default=5, ge=1, le=50),
    include_unborrowed: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.get_most_borrowed_books(
        limit=limit,
        include_unborrowed=include_unborrowed
    )



@router.get(
    "/top-members",
    response_model=list[TopMemberResponse]
)
def get_top_members(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    service = ReportService(db)
    return service.get_top_members(limit=limit)



@router.get(
    "/overdue-loans",
    response_model=list[OverdueLoanResponse]
)
def get_overdue_loans(
    min_days_overdue: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    service = ReportService(db)

    return service.get_overdue_loans(
        min_days_overdue=min_days_overdue
    )
