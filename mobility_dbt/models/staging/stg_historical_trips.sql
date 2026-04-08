SELECT
    -- ID
    id::text AS trip_id,

    -- station
    eva::text AS station_id,

    -- station_name,

    -- final_destination_station AS destination_station,

    -- planned time (departure öncelikli, fallback arrival)
    COALESCE(
        departure_planned_time,
        arrival_planned_time
    )::timestamp AS planned_time,

    -- actual time (change = actual)
    COALESCE(
        departure_change_time,
        arrival_change_time
    )::timestamp AS actual_time,

    -- delay (clamp negatives to 0 — early arrivals treated as on-time, consistent with stg_realtime_trips)
    GREATEST(delay_in_min::int, 0) AS delay_minutes,

    time::timestamp AS ingestion_time,

    -- feature engineering 👇
    EXTRACT(HOUR FROM COALESCE(departure_planned_time, arrival_planned_time)) AS hour,

    EXTRACT(DOW FROM COALESCE(departure_planned_time, arrival_planned_time)) AS day_of_week,

    CASE
        WHEN EXTRACT(DOW FROM COALESCE(departure_planned_time, arrival_planned_time)) IN (0,6)
        THEN TRUE ELSE FALSE
    END AS is_weekend,

    CASE
        WHEN delay_in_min > 0 THEN TRUE
        ELSE FALSE
    END AS is_delayed,

    CASE
        WHEN delay_in_min IS NULL THEN 'unknown'
        WHEN delay_in_min <= 0 THEN 'on_time'
        WHEN delay_in_min <= 5 THEN 'minor'
        WHEN delay_in_min <= 15 THEN 'medium'
        ELSE 'major'
    END AS delay_bucket

FROM {{ source('raw', 'historical_trips') }}

-- sadece Münih (opsiyonel ama önerilir)
WHERE station_name = 'München Hbf'
   OR final_destination_station = 'München Hbf'