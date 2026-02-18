from typing import Optional
from datetime import datetime
import xml.etree.ElementTree as ET


def parse_db_time(time_str: Optional[str]) -> Optional[datetime]:
    """
    Parses Deutsche Bahn timestamp format: YYMMDDHHMM
    Returns datetime object or None.
    """
    if not time_str:
        return None

    try:
        return datetime.strptime(time_str, "%y%m%d%H%M")
    except ValueError:
        return None

def parse_plan(xml_data: str) -> dict:
    root = ET.fromstring(xml_data)

    trips = {}
    for s in root.findall("s"):
        ar = s.find("ar")
        if ar is None:
            continue

        trip_id = s.attrib.get("id")
        planned_raw = ar.attrib.get("pt")

        if trip_id and planned_raw:
            trips[trip_id] = {
                "trip_id": trip_id,
                "planned": parse_db_time(planned_raw),
                "actual": None
            }

    return trips

def parse_changes(xml_data: str) -> dict:
    root = ET.fromstring(xml_data)

    updates = {}
    for s in root.findall("s"):
        ar = s.find("ar")
        if ar is None:
            continue

        trip_id = s.attrib.get("id")
        changed_raw = ar.attrib.get("ct")

        if trip_id and changed_raw:
            updates[trip_id] = parse_db_time(changed_raw)

    return updates