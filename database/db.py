import os
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# Determine project root and default DB path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DB_PATH = DATA_DIR / "meetflow.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = DEFAULT_DB_URL
elif DATABASE_URL.startswith("sqlite:///./"):
    # Resolve relative sqlite path relative to PROJECT_ROOT
    rel_path = DATABASE_URL.replace("sqlite:///./", "")
    full_path = PROJECT_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{full_path.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from database.models import Base
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """Generator function for sessions if needed."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
