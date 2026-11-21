import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
        "timeout": 60.0  # 60 second timeout for lock release
    }

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Configure SQLite for high concurrency (WAL mode + 60s busy timeout)
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")       # Write-Ahead Logging for concurrent read/write
        cursor.execute("PRAGMA synchronous=NORMAL")      # Optimal durability with minimal lock time
        cursor.execute("PRAGMA busy_timeout=60000")      # Wait up to 60,000 ms before throwing locked error
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
