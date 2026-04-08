from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and ensure it is closed after use.
    Used as a FastAPI dependency with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
