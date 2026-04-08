from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    station_id: str
    hour: int = Field(ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(ge=0, le=6, description="Day of week: 0=Sunday, 6=Saturday")
    is_weekend: bool


class PredictionResponse(BaseModel):
    predicted_bucket: str
    probabilities: dict[str, float]
    model_trained_at: str | None
