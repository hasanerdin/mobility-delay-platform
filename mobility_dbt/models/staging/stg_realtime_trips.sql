WITH base AS(
    SELECT
        trip_id::text AS trip_id,
        station_id::text AS station_id,
        -- station_name,
        -- destination_station,
        planned_time,
        actual_time,
        GREATEST(delay_minutes, 0) AS delay_minutes,
        ingestion_timestamp
    FROM {{ source('raw', 'trips') }}
)

SELECT
    *,

    EXTRACT(HOUR FROM planned_time) AS hour,
    EXTRACT(DOW FROM planned_time) AS day_of_week,

    CASE 
        WHEN EXTRACT(DOW FROM planned_time) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend,

    CASE 
        WHEN delay_minutes > 0 THEN TRUE
        ELSE FALSE
    END AS is_delayed,

    CASE 
        WHEN delay_minutes IS NULL THEN 'unknown'
        WHEN delay_minutes = 0 THEN 'on_time'
        WHEN delay_minutes <= 5 THEN 'minor'
        WHEN delay_minutes <= 15 THEN 'medium'
        ELSE 'major'
    END AS delay_bucket
    
FROM base
WHERE planned_time IS NOT NULL