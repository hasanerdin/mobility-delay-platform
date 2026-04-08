"""
Integration tests for the FastAPI application.

These tests use FastAPI's TestClient to send real HTTP requests.
The database dependency is replaced via conftest.py (dependency_overrides),
and repository functions are patched to return controlled data — so no
PostgreSQL connection is needed.
"""
from unittest.mock import patch

# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------
# health.py uses engine.connect() directly (not the get_db dependency),
# so we patch it here to avoid needing a real database in CI.

def test_health_returns_200(client):
    with patch("app.api.health.engine.connect"):
        response = client.get("/health")
    assert response.status_code == 200


def test_health_response_shape(client):
    with patch("app.api.health.engine.connect"):
        response = client.get("/health")
    body = response.json()
    assert "status" in body
    assert "timestamp" in body
    assert "database" in body


# ---------------------------------------------------------------------------
# /stations
# ---------------------------------------------------------------------------

MOCK_STATIONS = ["8000261", "8000105", "8000080"]

def test_list_stations_returns_200(client):
    with patch("app.api.routes.delay_repo.get_stations", return_value=MOCK_STATIONS):
        response = client.get("/stations")
    assert response.status_code == 200


def test_list_stations_returns_list_of_strings(client):
    with patch("app.api.routes.delay_repo.get_stations", return_value=MOCK_STATIONS):
        response = client.get("/stations")
    assert response.json() == MOCK_STATIONS


# ---------------------------------------------------------------------------
# /delays/by-hour
# ---------------------------------------------------------------------------

MOCK_HOURLY = [
    {"hour": 8, "total_trips": 10, "avg_delay": 3.5, "delayed_trips": 4, "delay_rate": 0.4},
    {"hour": 9, "total_trips": 15, "avg_delay": 5.2, "delayed_trips": 7, "delay_rate": 0.47},
]

def test_delays_by_hour_returns_200(client):
    with patch("app.api.routes.delay_repo.get_delays_by_hour", return_value=MOCK_HOURLY):
        response = client.get("/delays/by-hour?station_id=8000261")
    assert response.status_code == 200


def test_delays_by_hour_response_shape(client):
    with patch("app.api.routes.delay_repo.get_delays_by_hour", return_value=MOCK_HOURLY):
        response = client.get("/delays/by-hour?station_id=8000261")
    rows = response.json()
    assert len(rows) == 2
    assert rows[0]["hour"] == 8
    assert rows[0]["avg_delay"] == 3.5


def test_delays_by_hour_missing_station_param_returns_422(client):
    # FastAPI returns 422 Unprocessable Entity when a required query param is missing
    response = client.get("/delays/by-hour")
    assert response.status_code == 422


def test_delays_by_hour_unknown_station_returns_404(client):
    with patch("app.api.routes.delay_repo.get_delays_by_hour", return_value=[]):
        response = client.get("/delays/by-hour?station_id=UNKNOWN")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# /delays/top-delayed
# ---------------------------------------------------------------------------

MOCK_TOP = [
    {"station_id": "8000261", "total_trips": 100, "avg_delay": 8.1, "delayed_trips": 60, "delay_rate": 0.6},
]

def test_top_delayed_returns_200(client):
    with patch("app.api.routes.delay_repo.get_top_delayed_stations", return_value=MOCK_TOP):
        response = client.get("/delays/top-delayed")
    assert response.status_code == 200


def test_top_delayed_limit_above_max_returns_422(client):
    # limit is capped at 50 via Query(le=50)
    response = client.get("/delays/top-delayed?limit=100")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /predict
# ---------------------------------------------------------------------------

MOCK_PREDICTION = {
    "predicted_bucket": "minor",
    "probabilities": {"on_time": 0.3, "minor": 0.4, "medium": 0.2, "major": 0.1},
    "model_trained_at": "2026-04-08T00:00:00+00:00",
}

def test_predict_returns_200(client):
    with patch("app.api.routes.prediction_service.predict", return_value=MOCK_PREDICTION):
        response = client.post("/predict", json={
            "station_id": "8000261",
            "hour": 8,
            "day_of_week": 1,
            "is_weekend": False,
        })
    assert response.status_code == 200


def test_predict_response_shape(client):
    with patch("app.api.routes.prediction_service.predict", return_value=MOCK_PREDICTION):
        response = client.post("/predict", json={
            "station_id": "8000261",
            "hour": 8,
            "day_of_week": 1,
            "is_weekend": False,
        })
    body = response.json()
    assert body["predicted_bucket"] == "minor"
    assert "probabilities" in body
    assert "model_trained_at" in body


def test_predict_invalid_hour_returns_422(client):
    # hour must be 0–23
    response = client.post("/predict", json={
        "station_id": "8000261",
        "hour": 25,
        "day_of_week": 1,
        "is_weekend": False,
    })
    assert response.status_code == 422


def test_predict_model_not_found_returns_503(client):
    with patch(
        "app.api.routes.prediction_service.predict",
        side_effect=FileNotFoundError("Model not found"),
    ):
        response = client.post("/predict", json={
            "station_id": "8000261",
            "hour": 8,
            "day_of_week": 1,
            "is_weekend": False,
        })
    assert response.status_code == 503
