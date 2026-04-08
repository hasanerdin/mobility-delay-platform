from datetime import date

from pydantic import BaseModel


class DelayByHour(BaseModel):
    """Delay statistics for a station broken down by hour of day."""
    hour: int
    total_trips: int
    avg_delay: float
    delayed_trips: int
    delay_rate: float


class DelaySummaryRow(BaseModel):
    """Daily delay summary for a station at a specific hour."""
    date: date
    station_id: str
    hour: int
    day_of_week: int
    is_weekend: bool
    total_trips: int
    avg_delay: float
    delayed_trips: int
    delay_rate: float


class StationDelayStats(BaseModel):
    """Aggregated delay stats per station, used for top-delayed ranking."""
    station_id: str
    total_trips: int
    avg_delay: float
    delayed_trips: int
    delay_rate: float
