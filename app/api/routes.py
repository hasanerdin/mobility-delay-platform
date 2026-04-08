from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories import delays as delay_repo
from app.schemas.delays import DelayByHour, DelaySummaryRow, StationDelayStats
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services import prediction as prediction_service

router = APIRouter(tags=["delays"])


@router.get("/stations", response_model=list[str])
def list_stations(db: Annotated[Session, Depends(get_db)]):
    """Return all station IDs that have analytics data."""
    return delay_repo.get_stations(db)


@router.get("/delays/by-hour", response_model=list[DelayByHour])
def delays_by_hour(
    station_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Return hourly delay breakdown for a station.

    Example: GET /delays/by-hour?station_id=8000261
    """
    rows = delay_repo.get_delays_by_hour(db, station_id)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for station '{station_id}'",
        )
    return rows


@router.get("/delays/summary", response_model=list[DelaySummaryRow])
def delay_summary(
    station_id: str,
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = Query(default=None, description="Filter from this date (YYYY-MM-DD)"),
    end_date: date | None = Query(default=None, description="Filter up to this date (YYYY-MM-DD)"),
):
    """
    Return daily delay summary for a station with optional date range filter.

    Example: GET /delays/summary?station_id=8000261&start_date=2024-01-01
    """
    rows = delay_repo.get_delay_summary(db, station_id, start_date, end_date)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary data found for station '{station_id}'",
        )
    return rows


@router.get("/delays/top-delayed", response_model=list[StationDelayStats])
def top_delayed_stations(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=10, ge=1, le=50, description="Number of stations to return"),
):
    """
    Return stations ranked by average delay, highest first.

    Example: GET /delays/top-delayed?limit=5
    """
    return delay_repo.get_top_delayed_stations(db, limit)


@router.post("/predict", response_model=PredictionResponse, tags=["ml"])
def predict_delay(body: PredictionRequest):
    """
    Predict the delay bucket for a trip given station, hour, and day.

    Returns the predicted class (on_time / minor / medium / major)
    and the probability for each class.

    Example:
        POST /predict
        {"station_id": "8000261", "hour": 8, "day_of_week": 1, "is_weekend": false}
    """
    try:
        result = prediction_service.predict(
            station_id=body.station_id,
            hour=body.hour,
            day_of_week=body.day_of_week,
            is_weekend=body.is_weekend,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
