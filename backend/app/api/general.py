from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/welcome")
def home():
    return {
        "message": "Welcome to LibraFlow API"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "LibraFlow"
    }