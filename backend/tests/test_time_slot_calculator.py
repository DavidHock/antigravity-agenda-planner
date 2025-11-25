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


def test_one_hour_exchange_meeting_for_dev_research():
    """Exactly 60 minutes should be treated as a scheduled session."""
    schedule = calculate_time_slots(
        "2024-06-10T11:00:00",
        "2024-06-10T12:00:00",
    )

    assert schedule["type"] == "scheduled"
    day = schedule["days"][0]
    assert day["start_time"].endswith("11:00")
    assert day["end_time"].endswith("12:00")


def test_ninety_minute_innovation_lab_customer_session():
    """90 minute Stablenet lab meeting should be scheduled without dinner."""
    schedule = calculate_time_slots(
        "2024-07-02T13:00:00",
        "2024-07-02T14:30:00",
    )

    assert schedule["type"] == "scheduled"
    day = schedule["days"][0]
    assert day["start_time"].endswith("13:00")
    assert day["end_time"].endswith("14:30")
    assert not any(slot["type"] == "social" for slot in day["slots"])


def test_half_day_research_team_retreat():
    """Half day retreat should include lunch but no dinner."""
    schedule = calculate_time_slots(
        "2024-08-15T08:30:00",
        "2024-08-15T14:00:00",
    )

    day = schedule["days"][0]
    slot_types = [slot["type"] for slot in day["slots"]]
    assert "lunch_break" in slot_types
    assert not any(slot["type"] == "social" for slot in day["slots"])


def test_single_day_meeting_skips_dinner_when_ending_early():
    """Single-day sessions ending before 17:30 should not add the dinner slot."""
    schedule = calculate_time_slots(
        "2024-05-01T09:00:00",
        "2024-05-01T16:00:00",
    )

    day = schedule["days"][0]
    assert schedule["type"] == "scheduled"
    assert not any(slot["type"] == "social" for slot in day["slots"])


def test_single_day_meeting_adds_dinner_for_late_sessions():
    """Single-day sessions ending late should include the social dinner."""
    schedule = calculate_time_slots(
        "2024-05-01T09:00:00",
        "2024-05-01T19:30:00",
    )

    day = schedule["days"][0]
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


def test_two_and_half_day_sustainet_plenary():
    """2.5 day plenary should have dinners on full days only."""
    schedule = calculate_time_slots(
        "2024-09-04T09:00:00",
        "2024-09-06T15:00:00",
    )

    assert schedule["type"] == "multi_day"
    assert len(schedule["days"]) == 3

    first_two = schedule["days"][:-1]
    final_day = schedule["days"][-1]

    for day in first_two:
        assert any(slot["type"] == "social" for slot in day["slots"])

    assert not any(slot["type"] == "social" for slot in final_day["slots"])


def test_times_are_rounded_to_quarter_hours():
    """Start and end times should be rounded to 15 minute intervals."""
    schedule = calculate_time_slots(
        "2024-05-01T09:07:00",
        "2024-05-01T10:04:00",
    )

    day = schedule["days"][0]
    assert day["start_time"].endswith("09:00")
    assert day["end_time"].endswith("10:00")

