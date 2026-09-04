import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base
from app.utils.logger import logger

# Default to SQLite local database if DATABASE_URL is not set or if Postgres is unreachable
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = (BASE_DIR / "forensics.db").as_posix()

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 15}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=False
    )
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Could not connect to configured DATABASE_URL ({DATABASE_URL}): {e}. Falling back to local SQLite.")
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
    connect_args = {"check_same_thread": False, "timeout": 15}
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# Enable foreign keys and WAL mode for SQLite
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize database tables."""
    # Ensure upload directory exists
    upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables initialized successfully. Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
