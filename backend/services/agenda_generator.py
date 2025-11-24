from openai import OpenAI
from typing import List, Optional
from .researcher import perform_research

# Point to the local LM Studio instance
client = OpenAI(base_url="http://host.docker.internal:1234/v1", api_key="lm-studio")

from datetime import datetime

async def generate_agenda_content(topic: str, start_time: str, end_time: str, email_content: Optional[str], file_contents: List[str]) -> str:
    
    # Calculate duration
    try:
        # Handle both Z-suffixed (UTC) and local ISO strings
        start_clean = start_time.replace('Z', '')
        end_clean = end_time.replace('Z', '')
        start_dt = datetime.fromisoformat(start_clean)
        end_dt = datetime.fromisoformat(end_clean)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        duration_str = f"{int(duration_minutes)} minutes"
    except Exception as e:
        duration_str = "Unknown duration"
        start_dt = None
        end_dt = None

    # 1. Identify research needs
    research_query = f"Best practices for meeting agenda: {topic}"
    research_results = perform_research(research_query)

    # 2. Construct the prompt
    context_str = ""
    if email_content:
        context_str += f"\n\nEmail Context:\n{email_content}"
    
    if file_contents:
        context_str += "\n\nFile Contents:\n" + "\n---\n".join(file_contents)

    prompt = f"""
    You are an expert meeting facilitator. Create a detailed agenda for a meeting.
    
    **Meeting Details:**
    - Topic: {topic}
    - Start Time: {start_time}
    - End Time: {end_time}
    - Total Duration: {duration_str}
    
    **Context & Materials:**
    {context_str}
    
    **Research Insights:**
    {research_results}
    
    **Strict Scheduling Rules:**
    1. **Coffee Breaks**: If the meeting is longer than 120 minutes, insert a 30-minute coffee break every 90-120 minutes.
    2. **Lunch Break**: If the meeting time spans across the 12:00 - 13:00 (1:00 PM) window, you MUST insert a 60-minute Lunch Break around that time.
    3. **Time Slots**: Ensure all items have specific start and end times that fit within {start_time} to {end_time}.
    
    **Instructions:**
    - Create a structured agenda.
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
