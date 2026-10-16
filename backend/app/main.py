from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import general, info, books, members, loans


app = FastAPI(
    title="LibraFlow API",
    description="REST API for library Management System",
    version="1.0.0"
)

app.include_router(general.router)
app.include_router(info.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)


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








