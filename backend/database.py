# SQLAlchemy engine, session factory, and Base declarative class

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base  # noqa: F401 — re-exported for use in main.py

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dashboard.db")

# SQLite processes one write at a time and by default enforces that a connection
# is only used on the thread that created it. FastAPI runs request handlers on
# worker threads that differ from the main thread, so we disable that check.
# This is safe here because SQLAlchemy's session-per-request pattern ensures
# connections are not shared across threads concurrently.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
