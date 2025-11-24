from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
from services.agenda_generator import generate_agenda_content
from icalendar import Calendar, Event, vText
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agenda Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgendaRequest(BaseModel):
    topic: str
    duration: str
    email_content: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/generate-agenda")
async def generate_agenda(
    topic: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    language: str = Form("DE"),
    email_content: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
):
    try:
        file_contents = []
        if files:
            for file in files:
                content = await file.read()
                try:
                    file_contents.append(content.decode("utf-8"))
                except UnicodeDecodeError:
                    file_contents.append(f"[Binary file: {file.filename}]")

        agenda = await generate_agenda_content(topic, start_time, end_time, language, email_content, file_contents)
        return {"agenda": agenda}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/create-ics")
async def create_ics_get(
    topic: str,
    start_time: str,
    end_time: str,
    location: str,
    agenda_content: str
):
    # Call the POST version with the same logic
    return await create_ics(topic, start_time, end_time, location, agenda_content)

@app.post("/create-ics")
async def create_ics(
    topic: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    location: str = Form(...),
    agenda_content: str = Form(...)
):
    try:
        # Parse times to create filename
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', ''))
            year = start_dt.year
            month = str(start_dt.month).zfill(2)
            day = str(start_dt.day).zfill(2)
            hours = str(start_dt.hour).zfill(2)
            minutes = str(start_dt.minute).zfill(2)
            
            # Sanitize topic for filename
            import re
            sanitized_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic).strip()
            sanitized_topic = re.sub(r'\s+', ' ', sanitized_topic)[:50]
            
            filename = f"{year}-{month}-{day} {hours}-{minutes} {sanitized_topic}.ics"
        except:
            filename = "meeting_agenda.ics"
        
        cal = Calendar()
        cal.add('prodid', '-//Agenda Planner//mxm.dk//')
        cal.add('version', '2.0')

        event = Event()
        event.add('summary', topic)
        
        # Parse times (assuming local ISO strings from frontend)
        end_dt = datetime.fromisoformat(end_time.replace('Z', ''))
        
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('dtstamp', datetime.now())
        event.add('location', vText(location))
        
        # Format agenda content as plain text with simple formatting
        try:
            import json
            agenda_data = json.loads(agenda_content)
            
            # Build plain text description
            text_parts = []
            text_parts.append(agenda_data.get('title', 'Meeting Agenda'))
            text_parts.append("=" * len(text_parts[0]))
            text_parts.append("")
            
            if 'summary' in agenda_data:
                text_parts.append(agenda_data['summary'])
                text_parts.append("")
            
            # Handle Multi-day
            if 'days' in agenda_data:
                for i, day in enumerate(agenda_data['days']):
                    text_parts.append(f"DAY {i+1} - {day.get('date', '')}")
                    text_parts.append("-" * 40)
                    
                    for item in day.get('items', []):
                        time_slot = item.get('time_slot', '')
                        title = item.get('title', '')
                        duration = item.get('duration', '')
                        description = item.get('description', '')
                        
                        # Format each item
                        if time_slot:
                            header = f"{time_slot} - {title}"
                            if duration:
                                header += f" ({duration} mins)"
                            text_parts.append(header)
                        else:
                            text_parts.append(f"* {title}")
                            
                        if description:
                            text_parts.append(f"  {description}")
                        text_parts.append("")
                    text_parts.append("")
            
            # Handle Simple List or Single Day
            elif 'items' in agenda_data:
                text_parts.append("AGENDA ITEMS:")
                text_parts.append("-" * 40)
                text_parts.append("")
                for item in agenda_data['items']:
                    time_slot = item.get('time_slot', '')
                    title = item.get('title', '')
                    duration = item.get('duration', '')
                    description = item.get('description', '')
                    
                    # Format each item
                    if time_slot:
                        header = f"{time_slot} - {title}"
                        if duration:
                            header += f" ({duration} mins)"
                        text_parts.append(header)
                    else:
                        text_parts.append(f"* {title}")
                        
                    if description:
                        text_parts.append(f"  {description}")
                    text_parts.append("")
            
            plain_description = "\n".join(text_parts)
            event.add('description', plain_description)
        except Exception as e:
            # Fallback to plain text if JSON parsing fails
            print(f"Error parsing agenda JSON: {e}")
            event.add('description', agenda_content)
        
        cal.add_component(event)

        # Use both filename and filename* for maximum compatibility
        from urllib.parse import quote
        encoded_filename = quote(filename)
        
        return Response(
            content=cal.to_ical(),
            media_type="text/calendar",
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
