from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_stations(db: Session) -> list[str]:
    """Return all station IDs that have analytics data."""
    rows = db.execute(
        text("SELECT DISTINCT station_id FROM analytics.fact_delay ORDER BY station_id")
    ).fetchall()
    return [row[0] for row in rows]


def get_delays_by_hour(db: Session, station_id: str) -> list[dict]:
    """
    Return hourly delay breakdown for a station.
    Reads from analytics.fact_delay which is pre-aggregated by dbt.
    """
    rows = db.execute(
        text("""
            SELECT
                hour,
                total_trips,
                COALESCE(avg_delay, 0)       AS avg_delay,
                delayed_trips,
                ROUND(
                    delayed_trips::numeric / NULLIF(total_trips, 0),
                    2
                )                            AS delay_rate
            FROM analytics.fact_delay
            WHERE station_id = :station_id
            ORDER BY hour
        """),
        {"station_id": station_id},
    ).fetchall()
    return [row._mapping for row in rows]


def get_delay_summary(
    db: Session,
    station_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    """
    Return daily delay summary rows for a station, with optional date range.
    Reads from analytics.fact_delay_summary.
    """
    query = """
        SELECT
            date,
            station_id,
            hour,
            day_of_week,
            is_weekend,
            total_trips,
            COALESCE(avg_delay, 0) AS avg_delay,
            delayed_trips,
            COALESCE(delay_rate, 0) AS delay_rate
        FROM analytics.fact_delay_summary
        WHERE station_id = :station_id
    """
    params: dict = {"station_id": station_id}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY date DESC, hour"

    rows = db.execute(text(query), params).fetchall()
    return [row._mapping for row in rows]


def get_top_delayed_stations(db: Session, limit: int = 10) -> list[dict]:
    """
    Return stations ranked by average delay, descending.
    Aggregates across all hours from analytics.fact_delay.
    """
    rows = db.execute(
        text("""
            SELECT
                station_id,
                SUM(total_trips)                                            AS total_trips,
                ROUND(AVG(avg_delay), 2)                                    AS avg_delay,
                SUM(delayed_trips)                                          AS delayed_trips,
                ROUND(
                    SUM(delayed_trips)::numeric / NULLIF(SUM(total_trips), 0),
                    2
                )                                                           AS delay_rate
            FROM analytics.fact_delay
            GROUP BY station_id
            ORDER BY avg_delay DESC
            LIMIT :limit
        """),
        {"limit": limit},
    ).fetchall()
    return [row._mapping for row in rows]
