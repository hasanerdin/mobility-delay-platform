import json
from pathlib import Path

import joblib

from ml.features import build_single_input

MODEL_PATH = Path("model_registry/model.pkl")
METADATA_PATH = Path("model_registry/metadata.json")

# Module-level cache: the model is loaded once when the first prediction is
# requested, then reused for every subsequent call — no disk I/O per request.
_pipeline = None
_metadata: dict | None = None


def _load_model():
    global _pipeline, _metadata
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Model not found. Run: docker compose exec api python -m ml.train"
            )
        _pipeline = joblib.load(MODEL_PATH)
        if METADATA_PATH.exists():
            _metadata = json.loads(METADATA_PATH.read_text())


def predict(
    station_id: str,
    hour: int,
    day_of_week: int,
    is_weekend: bool,
) -> dict:
    _load_model()

    X = build_single_input(station_id, hour, day_of_week, is_weekend)

    predicted_bucket = _pipeline.predict(X)[0]

    # predict_proba returns a 2D array: [[p_class0, p_class1, ...]].
    # We zip with pipeline.classes_ to get a named dict.
    proba_array = _pipeline.predict_proba(X)[0]
    probabilities = {
        cls: round(float(prob), 4)
        for cls, prob in zip(_pipeline.classes_, proba_array)
    }

    return {
        "predicted_bucket": predicted_bucket,
        "probabilities": probabilities,
        "model_trained_at": _metadata.get("trained_at") if _metadata else None,
    }
