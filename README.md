# 🚆 Mobility Delay Platform

![CI](https://github.com/hasanerdin/mobility-delay-platform/actions/workflows/ci.yml/badge.svg)

An end-to-end data engineering platform for analyzing and predicting Deutsche Bahn railway delays. Ingests real-time API data, transforms it with dbt, orchestrates with Airflow, serves analytics via a FastAPI REST API, and visualizes results in a Streamlit dashboard — with a machine learning model for delay prediction.

> Built as a portfolio project to demonstrate production-level data engineering practices.

---

## Architecture

```
               Deutsche Bahn API (real-time)
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                     Ingestion Layer                       │
│  client → parser → merger → transformer → raw_loader     │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                    │
│                                                         │
│  raw.trips              ◄── real-time ingestion         │
│  raw.historical_trips   ◄── dbt seed (22-month dataset) │
│                                                         │
│  staging.stg_trips      ◄── dbt views (feature eng.)    │
│                                                         │
│  analytics.fact_delay         ◄── dbt tables            │
│  analytics.fact_delay_summary ◄── dbt tables            │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────┐     ┌───────────────────────┐
│      FastAPI REST API    │────▶│  Streamlit Dashboard  │
│  /stations               │     │  - KPI overview       │
│  /delays/by-hour         │     │  - Delay by hour      │
│  /delays/summary         │     │  - Station comparison │
│  /delays/top-delayed     │     └───────────────────────┘
│  /predict  (ML model)    │
└──────────────────────────┘

Airflow DAG (hourly): ingestion → dbt run → dbt test
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, Deutsche Bahn API (XML) |
| Storage | PostgreSQL 15 |
| Transformation | dbt (views + tables, seeds, schema tests) |
| Orchestration | Apache Airflow 2.9 |
| API | FastAPI, SQLAlchemy, Pydantic |
| Dashboard | Streamlit, Plotly |
| ML | scikit-learn (RandomForest Pipeline), joblib |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest, GitHub Actions CI |

---

## Data Layers (Medallion Architecture)

### Bronze — `raw` schema
| Table | Source | Description |
|---|---|---|
| `raw.trips` | Deutsche Bahn API | Real-time trips ingested hourly |
| `raw.historical_trips` | dbt seed (CSV) | 22 months of historical data, ~2000 Munich rows |

### Silver — `staging` schema (views)
| Model | Description |
|---|---|
| `stg_realtime_trips` | Cleaned real-time trips with feature columns |
| `stg_historical_trips` | Cleaned historical trips with feature columns |
| `stg_trips` | UNION ALL of both — single source of truth |

Feature columns added by staging: `hour`, `day_of_week`, `is_weekend`, `is_delayed`, `delay_bucket`

### Gold — `analytics` schema (tables)
| Model | Description |
|---|---|
| `fact_delay` | Avg delay aggregated by station + hour |
| `fact_delay_summary` | Daily delay stats by station + hour |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Database connectivity check |
| GET | `/stations` | List all station IDs with data |
| GET | `/delays/by-hour?station_id=` | Hourly delay breakdown |
| GET | `/delays/summary?station_id=&start_date=&end_date=` | Daily summary with date filter |
| GET | `/delays/top-delayed?limit=10` | Worst stations ranked by avg delay |
| POST | `/predict` | Predict delay bucket for a trip |

Interactive docs available at `http://localhost:8000/docs`

### Prediction endpoint example

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"station_id": "8000261", "hour": 8, "day_of_week": 1, "is_weekend": false}'
```

```json
{
  "predicted_bucket": "minor",
  "probabilities": {
    "major": 0.09,
    "medium": 0.18,
    "minor": 0.42,
    "on_time": 0.31
  },
  "model_trained_at": "2026-04-08T00:00:00+00:00"
}
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose

### 1. Clone and configure

```bash
git clone https://github.com/hasanerdin/mobility-delay-platform.git
cd mobility-delay-platform
cp .env.example .env
# Fill in your Deutsche Bahn API credentials in .env
```

### 2. Start all services

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| API | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |
| Airflow | http://localhost:8080 |

### 3. Initialize the data

```bash
# Load historical data and create analytics tables
docker compose exec api bash -c "cd /app/mobility_dbt && dbt seed --profiles-dir . && dbt run --profiles-dir ."
```

### 4. Train the ML model

```bash
docker compose exec api python -m ml.train
```

---

## Project Structure

```
mobility-delay-platform/
├── app/                    # FastAPI application
│   ├── api/                # Route handlers, dependencies
│   ├── repositories/       # SQL query layer
│   ├── schemas/            # Pydantic request/response models
│   └── services/           # ML inference service
├── ingestion/              # Deutsche Bahn API pipeline
│   ├── client.py           # HTTP requests
│   ├── parser.py           # XML parsing
│   ├── merger.py           # Plan + changes merge
│   ├── transformer.py      # Delay computation
│   └── raw_loader.py       # PostgreSQL insert
├── mobility_dbt/           # dbt project
│   ├── models/staging/     # Silver layer (views)
│   ├── models/analytics/   # Gold layer (tables)
│   └── seeds/              # Historical data CSV
├── ml/                     # ML pipeline
│   ├── features.py         # Feature engineering
│   └── train.py            # Model training script
├── dashboard/              # Streamlit app
│   ├── Home.py             # Overview page
│   ├── api_client.py       # API call wrapper
│   └── pages/              # Multi-page navigation
├── dags/                   # Airflow DAG
├── db/                     # Database init SQL
├── tests/                  # pytest test suite
│   ├── unit/               # Parser and transformer tests
│   └── integration/        # API endpoint tests
└── .github/workflows/      # GitHub Actions CI
```

---

## ML Model

Predicts the delay bucket (`on_time` / `minor` / `medium` / `major`) for a given trip.

**Features:** `station_id`, `hour`, `day_of_week`, `is_weekend`

**Model:** Random Forest Classifier inside a scikit-learn `Pipeline`
- `OneHotEncoder` on `station_id`
- `class_weight='balanced'` to handle class imbalance
- Trained on ~2000 rows from `staging.stg_trips`

**Test accuracy:** ~0.33 on 4-class problem (random baseline = 0.25)

---

## Testing

```bash
# Run all tests inside the container
docker compose exec api pytest tests/ -v

# Run unit tests only (no container needed if deps installed locally)
pytest tests/unit/ -v
```

34 unit tests + 2 integration tests covering:
- XML parser and time format handling
- Delay computation logic
- All API endpoints with mocked database
- Input validation (422 responses)
- Error handling (503 when model not found)

CI runs automatically on every push via GitHub Actions — no database required for the pytest job (DB dependency is mocked).

---

## Known Limitations

- **Late-arriving data:** Delays reported after the ingestion hour are not backfilled. The `ON CONFLICT DO NOTHING` constraint means a trip's delay stays `NULL` if the actual time wasn't available at ingestion time.
- **Single station:** Ingestion is hardcoded to München Hbf (EVA 8000261).
- **Small training set:** ML model trained on ~2000 rows. Accuracy would improve with the full historical dataset.
- **Full-refresh dbt models:** Analytics tables are recomputed from scratch on every run. Incremental materialization would improve performance at scale.

---

## Author

**Hasan Erdin**

Data Engineer — [GitHub](https://github.com/hasanerdin)
