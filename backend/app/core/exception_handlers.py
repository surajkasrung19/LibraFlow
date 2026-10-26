from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.exceptions import (
    LoanNotFoundError,
    LoanConflictError
)

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(LoanNotFoundError)
    async def handle_loan_not_found(
        request: Request,
        exc: LoanNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc)
            }
        )

    @app.exception_handler(LoanConflictError)
    async def handle_loan_conflict(
        request: Request,
        exc: LoanConflictError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc)
            }
        )