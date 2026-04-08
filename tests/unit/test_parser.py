"""Unit tests for ingestion/parser.py — no DB, no network."""
from datetime import datetime

import pytest

from ingestion.parser import parse_changes, parse_db_time, parse_plan

# ---------------------------------------------------------------------------
# parse_db_time
# ---------------------------------------------------------------------------

def test_parse_db_time_valid():
    # DB format: YYMMDDHHMM — "2604081430" = 2026-04-08 14:30
    result = parse_db_time("2604081430")
    assert result == datetime(2026, 4, 8, 14, 30)


def test_parse_db_time_none_returns_none():
    assert parse_db_time(None) is None


def test_parse_db_time_empty_string_returns_none():
    assert parse_db_time("") is None


def test_parse_db_time_invalid_format_returns_none():
    assert parse_db_time("not-a-date") is None


@pytest.mark.parametrize("time_str,expected", [
    ("2601010000", datetime(2026, 1, 1, 0, 0)),   # midnight
    ("2612312359", datetime(2026, 12, 31, 23, 59)),  # end of year
    ("2606151200", datetime(2026, 6, 15, 12, 0)),  # noon
])
def test_parse_db_time_various_inputs(time_str, expected):
    assert parse_db_time(time_str) == expected


# ---------------------------------------------------------------------------
# parse_plan
# ---------------------------------------------------------------------------

PLAN_XML = """<?xml version="1.0"?>
<timetable>
    <s id="trip-1">
        <ar pt="2604081430"/>
    </s>
    <s id="trip-2">
        <ar pt="2604081500"/>
    </s>
    <s id="trip-no-ar">
        <dp pt="2604081600"/>
    </s>
</timetable>
"""

def test_parse_plan_returns_trips_with_ar():
    result = parse_plan(PLAN_XML)
    assert "trip-1" in result
    assert "trip-2" in result


def test_parse_plan_skips_elements_without_ar():
    # trip-no-ar has only <dp>, no <ar> — should be excluded
    result = parse_plan(PLAN_XML)
    assert "trip-no-ar" not in result


def test_parse_plan_planned_time_is_parsed():
    result = parse_plan(PLAN_XML)
    assert result["trip-1"]["planned"] == datetime(2026, 4, 8, 14, 30)


def test_parse_plan_actual_time_is_none_initially():
    result = parse_plan(PLAN_XML)
    assert result["trip-1"]["actual"] is None


def test_parse_plan_empty_xml_returns_empty_dict():
    result = parse_plan("<timetable></timetable>")
    assert result == {}


# ---------------------------------------------------------------------------
# parse_changes
# ---------------------------------------------------------------------------

CHANGES_XML = """<?xml version="1.0"?>
<timetable>
    <s id="trip-1">
        <ar ct="2604081445"/>
    </s>
    <s id="trip-no-ct">
        <ar pt="2604081500"/>
    </s>
</timetable>
"""

def test_parse_changes_returns_changed_trips():
    result = parse_changes(CHANGES_XML)
    assert "trip-1" in result


def test_parse_changes_actual_time_is_parsed():
    result = parse_changes(CHANGES_XML)
    assert result["trip-1"] == datetime(2026, 4, 8, 14, 45)


def test_parse_changes_skips_elements_without_ct():
    result = parse_changes(CHANGES_XML)
    assert "trip-no-ct" not in result


def test_parse_changes_empty_xml_returns_empty_dict():
    result = parse_changes("<timetable></timetable>")
    assert result == {}
