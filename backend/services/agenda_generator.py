from openai import OpenAI
from typing import List, Optional
from .researcher import perform_research

# Point to the local LM Studio instance
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

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
    - Create a structured agenda with time slots.
    - Ensure the total time matches the duration.
    - Include specific discussion points based on the context.
    - Format the output in clean Markdown.
    """

    try:
        completion = client.chat.completions.create(
            model="local-model", # The model name is often ignored by LM Studio, but good to have
            messages=[
                {"role": "system", "content": "You are a helpful professional assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating agenda: {str(e)}. Ensure LM Studio is running on port 1234."
