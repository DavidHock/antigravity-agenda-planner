from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.agenda_generator import generate_agenda_content

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agenda Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4206"],
    allow_credentials=True,
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
    duration: str = Form(...),
    email_content: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
):
    try:
        # Process files if any
        file_contents = []
        if files:
            for file in files:
                content = await file.read()
                # Simple decoding for text-based files, might need more robust handling for PDFs/Docs
                try:
                    text_content = content.decode("utf-8")
                    file_contents.append(f"File: {file.filename}\nContent:\n{text_content}")
                except UnicodeDecodeError:
                    file_contents.append(f"File: {file.filename} (Binary content not fully supported yet)")

        agenda = await generate_agenda_content(topic, duration, email_content, file_contents)
        return {"agenda": agenda}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
