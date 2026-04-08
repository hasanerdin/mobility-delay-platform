from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.database import engine
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return HealthResponse(status="healthy", 
                              timestamp=datetime.now(timezone.utc),
                              database="connected")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )