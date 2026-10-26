from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import general, info, books, members, loans, reports
from app.core.middleware import request_logging_middleware
from app.core.exception_handlers import register_exception_handlers
from app.core.security import security_headers_middleware

app = FastAPI(
    title="LibraFlow API",
    description="REST API for library Management System",
    version="1.0.0"
)
register_exception_handlers(app)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(security_headers_middleware)


app.include_router(general.router)
app.include_router(info.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(reports.router)


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)
print("FRONTEND DIRECTORY:", FRONTEND_DIR)

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")








