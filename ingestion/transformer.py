

def compute_delay(trip: dict) -> dict:
    """
    Computes delay in minutes from planned and estimated times.
    Adds 'delay_minutes' key to trip dict.
    """

    planned_dt = trip.get("planned")
    actual_dt = trip.get("actual")

    delay_minutes = None
    if planned_dt and actual_dt:
        delta = (actual_dt - planned_dt).total_seconds() / 60
        delay_minutes = int(delta)

    # If estimated is not found, it is not correct to assume delay is 0
    # Therefore, we are leaving it None

    trip["delay_minutes"] = delay_minutes

    return trip
