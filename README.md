# 🚆 Mobility Delay Data Platform

A modern data engineering project that combines **real-time train data ingestion** with **historical datasets** to analyze railway delays.

---

# 📌 Overview

This project builds an end-to-end data platform that:

* Ingests real-time train data
* Enriches it with historical Deutsche Bahn data
* Transforms data using dbt
* Orchestrates pipelines with Airflow
* Stores everything in PostgreSQL

The result is a unified dataset for delay analysis and dashboards.

---

# 🏗 Architecture

```
Real-time API ──▶ Raw Layer ──▶ Staging Layer ──▶ Analytics Layer
                      ▲
                      │
          Historical Dataset (Parquet → CSV → dbt seed)
```

---

# ⚙️ Tech Stack

* **Python** – ingestion & data processing
* **PostgreSQL** – data warehouse
* **dbt** – transformations & modeling
* **Apache Airflow** – orchestration
* **Docker** – containerization

---

# 📊 Data Layers

## 🟢 Raw

* `raw.trips` → real-time API data
* `raw.historical_trips` → historical dataset (dbt seed)

## 🔵 Staging

* `stg_realtime_trips`
* `stg_historical_trips`
* `stg_trips` → unified dataset

## 🟣 Analytics

* `fact_delay`
* `fact_delay_summary`

---

# 🔄 Data Pipeline

1. **Ingestion (Airflow)**

   * Fetch real-time train data
   * Store in `raw.trips`

2. **Historical Data**

   * Parquet files processed
   * Filtered (Munich)
   * Loaded via dbt seed → `raw.historical_trips`

3. **Transformation (dbt)**

   * Clean & normalize data
   * Calculate delays
   * Create unified dataset

4. **Analytics**

   * Aggregate delay metrics
   * Prepare dashboard-ready tables

---

# 🚀 How to Run

## 1. Start services

```
docker compose up --build
```

## 2. Run dbt

```
dbt seed --full-refresh
dbt run
```

## 3. Access Airflow

```
http://localhost:8080
```

---

# 💾 Data Persistence

PostgreSQL uses Docker volumes to persist data:

```
volumes:
  db_data:
```

This ensures data is not lost when containers restart.

---

# 📈 Example Queries

```sql
SELECT delay_bucket, COUNT(*)
FROM staging.stg_trips
GROUP BY delay_bucket;
```

```sql
SELECT hour, AVG(delay_minutes)
FROM staging.stg_trips
GROUP BY hour;
```

---

# 🧠 Key Features

* Hybrid data model (historical + real-time)
* Modular dbt transformations
* Airflow orchestration
* Scalable architecture

---

# 🔥 Future Improvements

* Streamlit dashboard
* Multi-city support
* Data quality monitoring
* CI/CD pipeline

---

# 📌 Project Goal

To demonstrate a production-like data engineering workflow combining:

* Batch data (historical)
* Streaming data (real-time)
* Transformation & modeling
* Orchestration

---

# 👤 Author

Hasan Erdin

---

# ⭐ Notes

This project is designed as a portfolio piece to showcase real-world data engineering skills.
