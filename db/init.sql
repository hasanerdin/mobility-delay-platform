-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- RAW TABLE
CREATE TABLE IF NOT EXISTS raw.trips (
    id SERIAL PRIMARY KEY,
    trip_id TEXT NOT NULL,
    station_id TEXT NOT NULL,
    planned_time TIMESTAMP NOT NULL,
    actual_time TIMESTAMP,
    delay_minutes INTEGER,
    raw_payload JSONB,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STAGING TABLE
CREATE TABLE IF NOT EXISTS staging.trips_clean (
    trip_id TEXT,
    station_id TEXT,
    route_id TEXT,
    planned_time TIMESTAMP,
    delay_minutes INTEGER,
    hour INTEGER,
    weekday INTEGER
);

-- ANALYTICS TABLE
CREATE TABLE IF NOT EXISTS analytics.fact_delay (
    trip_id TEXT,
    station_id TEXT,
    route_id TEXT,
    planned_time TIMESTAMP,
    delay_minutes INTEGER,
    rolling_delay_1h FLOAT,
    rolling_delay_24h FLOAT
);
