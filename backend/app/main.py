from fastapi import FastAPI
from app.api import general, info, books


app = FastAPI(
    title="LibraFlow API",
    description="REST API for library Management System",
    version="1.0.0"
)

app.include_router(general.router)
app.include_router(info.router)
app.include_router(books.router)




