import os

import pandas as pd
import requests
import streamlit as st

# Inside Docker, the dashboard talks to the api service by its service name.
# Outside Docker (local dev), it falls back to localhost.
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _get(path: str, params: dict | None = None) -> list[dict]:
    """Make a GET request to the API and return parsed JSON."""
    try:
        response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Is the API service running?")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.status_code} — {e.response.text}")
        st.stop()


# @st.cache_data tells Streamlit: "cache the result of this function.
# Don't re-run it on every interaction — only when the arguments change."
# ttl=300 means the cache expires after 300 seconds (5 minutes).
@st.cache_data(ttl=300)
def get_stations() -> list[str]:
    return _get("/stations")


@st.cache_data(ttl=300)
def get_delays_by_hour(station_id: str) -> pd.DataFrame:
    rows = _get("/delays/by-hour", params={"station_id": station_id})
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def get_delay_summary(
    station_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    params = {"station_id": station_id}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    rows = _get("/delays/summary", params=params)
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def get_top_delayed_stations(limit: int = 10) -> pd.DataFrame:
    rows = _get("/delays/top-delayed", params={"limit": limit})
    return pd.DataFrame(rows)
