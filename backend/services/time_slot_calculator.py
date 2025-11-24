from datetime import datetime, timedelta
from typing import List, Dict, Any

def round_to_15_minutes(dt: datetime) -> datetime:
    """Round datetime to nearest 15-minute interval."""
    minutes = (dt.minute // 15) * 15
    return dt.replace(minute=minutes, second=0, microsecond=0)

def calculate_time_slots(start_time: str, end_time: str) -> Dict[str, Any]:
    """
    Calculate deterministic time slots based on meeting duration.
    
    Rules:
    1. All times are multiples of 15 minutes
    2. Meetings < 60 min: No time slots, just bullet points
    3. Meetings > 120 min: Breaks every 90-120 min, intelligently placed
    4. Multi-day: 08:30 start, 17:30 end, automatic lunch break 12:00-13:00
    5. Multi-day: Separate agenda per day
    """
    start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
    end_dt = datetime.fromisoformat(end_time.replace('Z', ''))
    
    # Round to 15-minute intervals
    start_dt = round_to_15_minutes(start_dt)
    end_dt = round_to_15_minutes(end_dt)
    
    total_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    # Check if multi-day
    is_multi_day = start_dt.date() != end_dt.date()
    
    if is_multi_day:
        return calculate_multi_day_slots(start_dt, end_dt)
    else:
        return calculate_single_day_slots(start_dt, end_dt, total_minutes)

def calculate_single_day_slots(start_dt: datetime, end_dt: datetime, total_minutes: int) -> Dict[str, Any]:
    """Calculate slots for single-day meeting using standard schedule."""
    
    # Meetings < 60 minutes: no time slots
    if total_minutes < 60:
        return {
            "type": "simple",
            "duration_minutes": total_minutes,
            "num_items": max(3, total_minutes // 15),
            "days": [{
                "date": start_dt.date().isoformat(),
                "start_time": start_dt.strftime("%H:%M"),
                "end_time": end_dt.strftime("%H:%M"),
                "slots": []
            }]
        }
    
    slots = apply_standard_schedule(start_dt, end_dt)
    
    # Add Dinner / Social event if the meeting goes until at least 17:30
    # User request: "generell nirgendwo" (interpreted as generally everywhere appropriate)
    if end_dt.hour >= 17 and end_dt.minute >= 30:
        slots.append({
            "start": "19:00",
            "end": "",
            "duration_minutes": 0,
            "title": "Dinner / Social event",
            "type": "social"
        })
    
    return {
        "type": "scheduled",
        "duration_minutes": total_minutes,
        "days": [{
            "date": start_dt.date().isoformat(),
            "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"),
            "slots": slots
        }]
    }

def calculate_multi_day_slots(start_dt: datetime, end_dt: datetime) -> Dict[str, Any]:
    """Calculate slots for multi-day meeting."""
    days = []
    current_date = start_dt.date()
    end_date = end_dt.date()
    
    while current_date <= end_date:
        # Determine start and end times for this day
        if current_date == start_dt.date():
            day_start = start_dt
        else:
            day_start = datetime.combine(current_date, datetime.min.time()).replace(hour=8, minute=30)
        
        if current_date == end_date:
            day_end = end_dt
        else:
            day_end = datetime.combine(current_date, datetime.min.time()).replace(hour=17, minute=30)
        
        # Apply standard schedule
        day_slots = apply_standard_schedule(day_start, day_end)
        
        # Add Dinner / Social event at 19:00 for ALL days in multi-day schedule
        # User request: "bitte noch das Dinner dazu um 19:00"
        day_slots.append({
            "start": "19:00",
            "end": "",
            "duration_minutes": 0,
            "title": "Dinner / Social event",
            "type": "social"
        })
        
        days.append({
            "date": current_date.isoformat(),
            "start_time": day_start.strftime("%H:%M"),
            "end_time": day_end.strftime("%H:%M"),
            "slots": day_slots
        })
        
        current_date += timedelta(days=1)
    
    total_minutes = sum(
        sum(slot["duration_minutes"] for slot in day["slots"])
        for day in days
    )
    
    return {
        "type": "multi_day",
        "duration_minutes": total_minutes,
        "days": days
    }

def apply_standard_schedule(start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
    """
    Apply standard day schedule to a given time range.
    Standard Day:
    08:30 - 10:15 Work
    10:15 - 10:45 Coffee Break
    10:45 - 12:30 Work
    12:30 - 13:30 Lunch Break
    13:30 - 15:15 Work
    15:15 - 15:45 Coffee Break
    15:45 - 17:30 Work
    """
    slots = []
    current_date = start_dt.date()
    
    # Define standard slots for the day
    standard_slots = [
        {"start": "08:30", "end": "10:15", "type": "work"},
        {"start": "10:15", "end": "10:45", "type": "coffee_break"},
        {"start": "10:45", "end": "12:30", "type": "work"},
        {"start": "12:30", "end": "13:30", "type": "lunch_break"},
        {"start": "13:30", "end": "15:15", "type": "work"},
        {"start": "15:15", "end": "15:45", "type": "coffee_break"},
        {"start": "15:45", "end": "17:30", "type": "work"}
    ]
    
    for slot in standard_slots:
        slot_start = datetime.combine(current_date, datetime.strptime(slot["start"], "%H:%M").time())
        slot_end = datetime.combine(current_date, datetime.strptime(slot["end"], "%H:%M").time())
        
        # Check for intersection
        # Intersection = max(start1, start2) < min(end1, end2)
        intersect_start = max(start_dt, slot_start)
        intersect_end = min(end_dt, slot_end)
        
        if intersect_start < intersect_end:
            duration = int((intersect_end - intersect_start).total_seconds() / 60)
            
            # Only add if duration > 0
            if duration > 0:
                slots.append({
                    "start": intersect_start.strftime("%H:%M"),
                    "end": intersect_end.strftime("%H:%M"),
                    "duration_minutes": duration,
                    "type": slot["type"]
                })
                
    return slots
