SELECT *
FROM {{ ref('stg_trips') }}
WHERE delay_minutes < 0