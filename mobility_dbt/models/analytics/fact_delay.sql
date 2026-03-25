SELECT
    station_id,
    hour,
    COUNT(*) AS total_trips,
    ROUND(AVG(delay_minutes), 2) AS avg_delay,
    SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS delayed_trips
FROM {{ ref('stg_trips') }}
GROUP BY station_id, hour