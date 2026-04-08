import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# These are the columns the model trains on and expects at inference time.
FEATURE_COLUMNS = ["hour", "day_of_week", "is_weekend", "station_id"]
TARGET_COLUMN = "delay_bucket"

# Only keep rows where the target is a known, meaningful label.
VALID_BUCKETS = ["on_time", "minor", "medium", "major"]


def load_training_data(db: Session) -> pd.DataFrame:
    """
    Load feature + target data from the staging layer.

    We read from staging.stg_trips (the UNION of realtime + historical),
    which already has all feature columns computed by dbt.
    We exclude rows where delay_bucket is 'unknown' (NULL delay — no label).
    """
    query = text("""
        SELECT
            hour,
            day_of_week,
            is_weekend,
            station_id,
            delay_bucket
        FROM staging.stg_trips
        WHERE delay_bucket IN ('on_time', 'minor', 'medium', 'major')
          AND hour IS NOT NULL
          AND day_of_week IS NOT NULL
          AND station_id IS NOT NULL
    """)
    rows = db.execute(query).fetchall()
    return pd.DataFrame(rows, columns=[*FEATURE_COLUMNS, TARGET_COLUMN])


def build_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Split a dataframe into X (features) and y (target).
    Called by both the training script and the prediction service.
    """
    X = df[FEATURE_COLUMNS].copy()
    X["is_weekend"] = X["is_weekend"].astype(bool)
    y = df[TARGET_COLUMN]
    return X, y


def build_single_input(
    station_id: str,
    hour: int,
    day_of_week: int,
    is_weekend: bool,
) -> pd.DataFrame:
    """
    Build a single-row feature dataframe for inference.
    Column order must match FEATURE_COLUMNS exactly.
    """
    return pd.DataFrame([{
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "station_id": station_id,
    }])
