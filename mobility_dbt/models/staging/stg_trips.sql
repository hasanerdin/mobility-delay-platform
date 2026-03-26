SELECT * FROM {{ ref('stg_realtime_trips') }}

UNION ALL

SELECT * FROM {{ ref('stg_historical_trips') }}