from ingestion.client import fetch_plans, fetch_changes
from ingestion.parser import parse_plan, parse_changes
from ingestion.merger import merge_plan_and_changes
from ingestion.transformer import compute_delay
from ingestion.raw_loader import insert_raw_trip

STATION_ID = "8000261" # München Hauptbahnhof

def run():
    plan_xml = fetch_plans(STATION_ID)
    change_xml = fetch_changes(STATION_ID)

    plan_trips = parse_plan(plan_xml)
    change_updates = parse_changes(change_xml) if change_xml else {}

    merged = merge_plan_and_changes(plan_trips, change_updates)

    for trip in merged:
        trip = compute_delay(trip)
        insert_raw_trip(trip)

    print(f"Inserted {len(merged)} trips")

if __name__ == "__main__":
    run()
