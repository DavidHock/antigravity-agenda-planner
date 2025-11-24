from openai import OpenAI
from typing import List, Optional
from .researcher import perform_research

# Point to the local LM Studio instance
client = OpenAI(base_url="http://host.docker.internal:1234/v1", api_key="lm-studio")

async def generate_agenda_content(topic: str, duration: str, email_content: Optional[str], file_contents: List[str]) -> str:
    
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
    - Duration: {duration}
    
    **Context & Materials:**
    {context_str}
    
    **Research Insights:**
    {research_results}
    
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
