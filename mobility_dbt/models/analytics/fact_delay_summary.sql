SELECT
    DATE(planned_time) AS date,
    station_id,
    hour,
    day_of_week,
    is_weekend,

    COUNT(*) AS total_trips,

    ROUND(AVG(delay_minutes), 2) AS avg_delay,

    SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS delayed_trips,

    ROUND(
        SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 1.0
        / COUNT(*),
        2
    ) AS delay_rate

FROM {{ ref('stg_trips') }}

GROUP BY
    DATE(planned_time),
    station_id,
    hour,
    day_of_week,
    is_weekend