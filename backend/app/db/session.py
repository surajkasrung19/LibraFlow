from pathlib import Path
import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker



BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_DATABASE_URL = (
    f"sqlite:///{(BASE_DIR / 'library.db').as_posix()}"
)

DATABASE_URL = os.getenv(
    "LIBRAFLOW_DATABASE_URL",
    DEFAULT_DATABASE_URL
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()