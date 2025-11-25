from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.time_slot_calculator import calculate_time_slots


def test_short_meeting_uses_simple_schedule():
    """Meetings under 60 minutes should produce a simple agenda."""
    schedule = calculate_time_slots(
        "2024-05-01T09:00:00",
        "2024-05-01T09:45:00",
    )

    assert schedule["type"] == "simple"
    assert schedule["duration_minutes"] == 45
    assert schedule["num_items"] >= 3
    assert schedule["days"][0]["slots"] == []


def test_single_day_meeting_generates_standard_slots():
    """Meetings longer than an hour should produce deterministic slots."""
    schedule = calculate_time_slots(
        "2024-05-01T08:30:00",
        "2024-05-01T17:30:00",
    )

    assert schedule["type"] == "scheduled"
    day = schedule["days"][0]
    slot_types = [slot["type"] for slot in day["slots"]]

    # Ensure the standard breaks are injected
    assert "coffee_break" in slot_types
    assert "lunch_break" in slot_types
    # Final social event should be appended when the meeting spans the evening
    assert any(slot["type"] == "social" for slot in day["slots"])


def test_multi_day_schedule_skips_dinner_on_short_final_day():
    """Dinner should be skipped on the last day if the meeting ends early."""
    schedule = calculate_time_slots(
        "2024-05-01T09:00:00",
        "2024-05-03T15:00:00",
    )

    assert schedule["type"] == "multi_day"
    assert len(schedule["days"]) == 3

    # First two days should still receive the dinner slot
    for day in schedule["days"][:-1]:
        assert any(slot["type"] == "social" for slot in day["slots"])

    # Final day ends mid-afternoon, so the dinner slot should be absent
    assert not any(slot["type"] == "social" for slot in schedule["days"][-1]["slots"])


def test_multi_day_schedule_keeps_dinner_when_final_day_runs_late():
    """If the final day goes into the evening, dinner should remain."""
    schedule = calculate_time_slots(
        "2024-05-01T09:00:00",
        "2024-05-03T20:00:00",
    )

    assert schedule["type"] == "multi_day"
    assert len(schedule["days"]) == 3
    assert any(slot["type"] == "social" for slot in schedule["days"][-1]["slots"])


def test_times_are_rounded_to_quarter_hours():
    """Start and end times should be rounded to 15 minute intervals."""
    schedule = calculate_time_slots(
        "2024-05-01T09:07:00",
        "2024-05-01T10:04:00",
    )

    day = schedule["days"][0]
    assert day["start_time"].endswith("09:00")
    assert day["end_time"].endswith("10:00")

