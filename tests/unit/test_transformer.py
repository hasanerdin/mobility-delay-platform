"""Unit tests for ingestion/transformer.py — no DB, no network."""
from datetime import datetime

from ingestion.transformer import compute_delay


def test_compute_delay_returns_correct_minutes():
    trip = {
        "planned": datetime(2026, 4, 8, 14, 30),
        "actual":  datetime(2026, 4, 8, 14, 45),
    }
    result = compute_delay(trip)
    assert result["delay_minutes"] == 15


def test_compute_delay_no_actual_returns_none():
    # If no actual time was reported, delay should be None — not 0.
    # Assuming zero would be wrong: we simply don't know.
    trip = {
        "planned": datetime(2026, 4, 8, 14, 30),
        "actual": None,
    }
    result = compute_delay(trip)
    assert result["delay_minutes"] is None


def test_compute_delay_no_planned_returns_none():
    trip = {
        "planned": None,
        "actual": datetime(2026, 4, 8, 14, 45),
    }
    result = compute_delay(trip)
    assert result["delay_minutes"] is None


def test_compute_delay_early_arrival_is_negative():
    # Train arrived 5 minutes early — raw delay is negative.
    # transformer does NOT clamp (clamping happens in dbt staging layer).
    trip = {
        "planned": datetime(2026, 4, 8, 14, 30),
        "actual":  datetime(2026, 4, 8, 14, 25),
    }
    result = compute_delay(trip)
    assert result["delay_minutes"] == -5


def test_compute_delay_on_time_is_zero():
    trip = {
        "planned": datetime(2026, 4, 8, 14, 30),
        "actual":  datetime(2026, 4, 8, 14, 30),
    }
    result = compute_delay(trip)
    assert result["delay_minutes"] == 0


def test_compute_delay_mutates_and_returns_trip():
    # compute_delay adds 'delay_minutes' to the existing dict and returns it.
    trip = {
        "planned": datetime(2026, 4, 8, 14, 30),
        "actual": datetime(2026, 4, 8, 14, 35)
    }
    result = compute_delay(trip)
    assert "delay_minutes" in result
    assert result is trip  # same object, not a copy
