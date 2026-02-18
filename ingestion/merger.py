from typing import List, Dict


def merge_plan_and_changes(plan_trips: List[Dict], change_updates: Dict) -> List[Dict]:
    for trip_id, actual in change_updates.items():
        if trip_id in plan_trips:
            plan_trips[trip_id]["actual"] = actual

    return list(plan_trips.values())