
from openai import OpenAI
from typing import Optional, List
import json
import re
from .researcher import perform_research

# Point to the local LM Studio instance
client = OpenAI(base_url="http://host.docker.internal:1234/v1", api_key="lm-studio")

from datetime import datetime

async def generate_agenda_content(topic: str, start_time: str, end_time: str, language: str, email_content: str = None, file_contents: list = None) -> str:
    """Generate agenda content for pre-calculated time slots."""
    from services.time_slot_calculator import calculate_time_slots
    
    # Calculate deterministic time slots
    schedule = calculate_time_slots(start_time, end_time)
    
    # Determine language instruction
    lang_instruction = "in German" if language == "DE" else "in English"
    
    # Build prompt based on schedule type
    if schedule["type"] == "simple":
        # Short meeting: just bullet points, no times
        prompt = f"""Create a simple meeting agenda {lang_instruction} for: {topic}

Meeting Duration: {schedule['duration_minutes']} minutes

Generate {schedule['num_items']} agenda points as a simple list.

"""
    else:
        # Scheduled meeting: fill in content for pre-calculated slots
        prompt = f"""Create a detailed meeting agenda {lang_instruction} for: {topic}

The time slots have been pre-calculated. Your job is to fill in appropriate content for each slot.

"""
        # Add day-by-day schedule
        for day_idx, day in enumerate(schedule["days"]):
            if schedule["type"] == "multi_day":
                prompt += f"\n**Day {day_idx + 1} ({day['date']}):**\n"
            
            for slot in day["slots"]:
                if slot["type"] == "lunch_break":
                    prompt += f"- {slot['start']} - {slot['end']}: Lunch Break (60 mins)\n"
                elif slot["type"] == "coffee_break":
                    prompt += f"- {slot['start']} - {slot['end']}: Coffee Break (30 mins)\n"
                elif slot["type"] == "social":
                    prompt += f"- {slot['start']}: Dinner / Social event\n"
                else:
                    prompt += f"- {slot['start']} - {slot['end']}: [FILL CONTENT] ({slot['duration_minutes']} mins)\n"
            prompt += "\n"
    
    if email_content:
        prompt += f"\nEmail Context:\n{email_content}\n"
    
    if file_contents:
        prompt += "\nAttached Files Content:\n"
        for content in file_contents:
            prompt += f"{content}\n"
    
    if schedule["type"] == "simple":
        prompt += f"""
Return a JSON object {lang_instruction} with this structure:
{{
    "title": "Meeting title {lang_instruction}",
    "summary": "Brief summary {lang_instruction}",
    "items": [
        {{
            "title": "Agenda point title {lang_instruction}",
            "description": "Brief description {lang_instruction}"
        }}
    ]
}}

All text must be {lang_instruction}.
"""
    else:
        prompt += f"""
Fill in the [FILL CONTENT] slots with appropriate agenda items {lang_instruction}.

Return a JSON object with this structure:
{{
    "title": "Meeting title {lang_instruction}",
    "summary": "Brief summary {lang_instruction}",
    "days": [
        {{
            "date": "YYYY-MM-DD",
            "start_time": "HH:MM",
            "end_time": "HH:MM",
            "items": [
                {{
                    "time_slot": "HH:MM - HH:MM",
                    "title": "Item title {lang_instruction}",
                    "description": "Description {lang_instruction}",
                    "duration": "X mins",
                    "type": "work|lunch_break|coffee_break"
                }}
            ]
        }}
    ]
}}

All text must be {lang_instruction}. Keep the exact time slots provided above.
"""

    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are a helpful professional assistant that outputs strict JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        content = completion.choices[0].message.content.strip()
        
        # Clean up potential markdown code blocks if the model ignores instructions
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return content.strip()
    except Exception as e:
        # Fallback JSON error
        import json
        return json.dumps({
            "title": "Error Generating Agenda",
            "summary": f"Could not generate structured agenda. Error: {str(e)}",
            "items": []
        })
