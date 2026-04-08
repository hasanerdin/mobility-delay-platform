"""
Training script for the delay bucket classifier.

Run from inside the API container:
    docker compose exec api python -m ml.train
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.core.database import SessionLocal
from ml.features import FEATURE_COLUMNS, build_feature_matrix, load_training_data

MODEL_DIR = Path("model_registry")
MODEL_PATH = MODEL_DIR / "model.pkl"
METADATA_PATH = MODEL_DIR / "metadata.json"


def train() -> None:
    print("Loading training data from staging.stg_trips...")
    db = SessionLocal()
    try:
        df = load_training_data(db)
    finally:
        db.close()

    print(f"Loaded {len(df):,} rows. Class distribution:")
    print(df["delay_bucket"].value_counts())

    X, y = build_feature_matrix(df)

    # Split into train (80%) and test (20%).
    # random_state=42 makes the split reproducible — same seed = same split every time.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ColumnTransformer: apply OneHotEncoder to station_id, passthrough everything else.
    # handle_unknown='ignore' means unseen stations at inference won't crash the model.
    preprocessor = ColumnTransformer(
        transformers=[
            ("station_ohe", OneHotEncoder(handle_unknown="ignore"), ["station_id"]),
        ],
        remainder="passthrough",  # hour, day_of_week, is_weekend pass through unchanged
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",  # penalize mistakes on rare classes more heavily
        )),
    ])

    print("\nTraining RandomForestClassifier...")
    pipeline.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    accuracy = report["accuracy"]
    print(f"\nTest accuracy: {accuracy:.3f}")
    print(classification_report(y_test, y_pred))

    # Save model
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    # Save metadata alongside the model so we always know what's in the registry
    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_rows": len(X_train),
        "test_accuracy": round(accuracy, 4),
        "features": FEATURE_COLUMNS,
        "target": "delay_bucket",
        "classes": list(pipeline.classes_),
        "model_type": "RandomForestClassifier",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))
    print(f"Metadata saved to {METADATA_PATH}")


if __name__ == "__main__":
    train()
