from openai import OpenAI
from typing import List, Optional
from .researcher import perform_research

# Point to the local LM Studio instance
client = OpenAI(base_url="http://host.docker.internal:1234/v1", api_key="lm-studio")

from datetime import datetime

async def generate_agenda_content(topic: str, start_time: str, end_time: str, language: str, email_content: str = None, file_contents: list = None) -> str:
    # Calculate duration
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    # Determine language instruction
    lang_instruction = "in German" if language == "DE" else "in English"
    
    # Build the prompt with break rules
    prompt = f"""Create a detailed meeting agenda {lang_instruction} for the following topic: {topic}

Meeting Duration: {duration_minutes} minutes
Start Time: {start_dt.strftime('%H:%M')}
End Time: {end_dt.strftime('%H:%M')}

IMPORTANT RULES FOR BREAKS:
1. If the meeting is longer than 120 minutes, include a 30-minute coffee break every 90-120 minutes
2. If the meeting spans the time between 12:00 PM and 1:00 PM, include a 60-minute lunch break during that time
3. Label breaks clearly as "Coffee Break" or "Lunch Break"

"""
    
    if email_content:
        prompt += f"\nEmail Context:\n{email_content}\n"
    
    if file_contents:
    - Ensure the total time matches the duration.
    - Return the result strictly as a valid JSON object.
    - Do not include any markdown formatting (like ```json ... ```) or extra text.
    
    **JSON Schema:**
    {{
        "title": "Meeting Title",
        "summary": "Brief summary of the meeting goal",
        "items": [
            {{
                "time_slot": "09:00 - 09:10",
                "title": "Introduction",
                "description": "Welcome and context setting",
                "duration": "10 mins"
            }}
        ]
    }}
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
