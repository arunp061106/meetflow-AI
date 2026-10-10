import os
import shutil
import tempfile
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def _is_dir_writable(path: Path) -> bool:
    """Test if a directory is writable by attempting to create and delete a probe file."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok")
        probe.unlink()
        return True
    except (OSError, PermissionError):
        return False

def resolve_db_path_and_url() -> tuple[Path, str]:
    """
    Intelligently resolves a writable database path and SQLAlchemy URL.
    Handles:
    - Custom DATABASE_URL from environment or Streamlit secrets (Postgres, remote, etc.)
    - Local project /data directory when writable
    - Read-only environments like Streamlit Community Cloud (/mount/src/) by falling back to /tmp
    """
    env_db_url = os.getenv("DATABASE_URL")
    if not env_db_url:
        try:
            import streamlit as st
            if "DATABASE_URL" in st.secrets:
                env_db_url = st.secrets["DATABASE_URL"]
        except Exception:
            pass

    # If external database (e.g. postgresql://, mysql://), pass through directly
    if env_db_url and not env_db_url.startswith("sqlite"):
        return Path("remote_db"), env_db_url

    # In-memory database requested
    if env_db_url and ":memory:" in env_db_url:
        return Path(":memory:"), env_db_url

    # Check if a custom relative sqlite path was provided
    if env_db_url and env_db_url.startswith("sqlite:///./"):
        rel_path = env_db_url.replace("sqlite:///./", "")
        custom_target = PROJECT_ROOT / rel_path
        if _is_dir_writable(custom_target.parent):
            return custom_target, f"sqlite:///{custom_target.as_posix()}"

    # Primary choice: Project data folder
    primary_data_dir = PROJECT_ROOT / "data"
    if _is_dir_writable(primary_data_dir):
        db_path = primary_data_dir / "meetflow.db"
    else:
        # Fallback for read-only deployments (Streamlit Cloud mounts, Docker containers, etc.)
        fallback_dir = Path(tempfile.gettempdir()) / "meetflow_data"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        db_path = fallback_dir / "meetflow.db"

        # If a pre-seeded db exists in repo, copy it to the writable temp directory
        seed_db = primary_data_dir / "meetflow.db"
        if seed_db.exists() and not db_path.exists():
            try:
                shutil.copy2(seed_db, db_path)
            except Exception:
                pass

    db_url = f"sqlite:///{db_path.as_posix()}"
    return db_path, db_url

DEFAULT_DB_PATH, DATABASE_URL = resolve_db_path_and_url()

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
