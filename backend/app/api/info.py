from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/info")
def info():
    return{
  "project": "LibraFlow",
  "backend": "FastAPI",
  "database": "SQLite",
  "version": "1.0.0"
}

