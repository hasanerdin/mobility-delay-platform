import requests
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from app.core.config import get_settings

settings = get_settings()

def fetch_plans(station_id: str):
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    date_str = now.strftime("%y%m%d")
    hour_str = now.strftime("%H")

    url = f"{settings.DB_URL}/plan/{station_id}/{date_str}/{hour_str}"
    
    headers = {
        "DB-Client-Id": settings.DB_CLIENT_ID,
        "DB-Api-Key": settings.DB_API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.text

def fetch_changes(station_id: str):
    url = f"{settings.DB_URL}/rchg/{station_id}"

    headers = {
        "DB-Client-Id": settings.DB_CLIENT_ID,
        "DB-Api-Key": settings.DB_API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.text
