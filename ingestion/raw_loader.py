from sqlalchemy import text
from app.core.database import engine
import json
from datetime import datetime

def json_serializer(obj) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return str(obj)

def insert_raw_trip(trip: dict):
    trip_id = trip.get("trip_id")
    planned = trip.get("planned")
    actual = trip.get("actual")
    delay = trip.get("delay_minutes")

    query = text("""
        INSERT INTO raw.trips(
                 trip_id,
                 station_id,
                 planned_time,
                 actual_time,
                 delay_minutes,
                 raw_payload
        )
        VALUES(
            :trip_id,
            :station_id,
            :planned_time,
            :actual_time,
            :delay_minutes,
            :raw_payload         
        )
        ON CONFLICT DO NOTHING
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "trip_id": trip_id,
            "station_id": "8000261",
            "planned_time": planned,
            "actual_time": actual,
            "delay_minutes": delay,
            "raw_payload": json.dumps(trip, default=json_serializer)
        })
