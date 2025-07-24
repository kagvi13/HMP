# agents/mcp_server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from tools.storage import Storage

app = FastAPI(title="HMP MCP-Agent API", version="0.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Storage()

# ======== MODELS ========

class NoteInput(BaseModel):
    text: str
    tags: Optional[List[str]] = []

class NoteOutput(BaseModel):
    id: int
    text: str
    tags: List[str]
    source: str
    read: int
    timestamp: str

class DiaryInput(BaseModel):
    text: str
    tags: Optional[List[str]] = []

class DiaryOutput(BaseModel):
    id: int
    text: str
    tags: List[str]
    timestamp: str

class DiaryListOutput(BaseModel):
    entries: List[DiaryOutput]

# ======== ROUTES ========

@app.get("/status")
def status():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/diary/write", response_model=dict)
def write_diary(entry: DiaryInput):
    db.write_diary_entry(entry.text, entry.tags)
    return {"result": "entry saved"}


@app.get("/diary/read", response_model=DiaryListOutput)
def read_diary(limit: int = 5, tag: Optional[str] = None):
    raw = db.read_diary_entries(limit=limit, tag_filter=tag)
    return {
        "entries": [
            {
                "id": r[0],
                "text": r[1],
                "tags": r[2].split(",") if r[2] else [],
                "timestamp": r[3]
            } for r in raw
        ]
    }

@app.delete("/diary/delete/{entry_id}")
def delete_diary(entry_id: int):
    db.delete_diary_entry_by_id(entry_id)
    return {"result": f"entry {entry_id} deleted"}


@app.post("/note/write", response_model=dict)
def write_note(note: NoteInput):
    db.write_note(note.text, note.tags)
    return {"result": "note saved"}


@app.get("/note/next", response_model=Optional[NoteOutput])
def get_next_note():
    note = db.get_first_unread_note()
    if note:
        note_id, text, tags, source, read, timestamp = note
        return {
            "id": note_id,
            "text": text,
            "tags": tags.split(",") if tags else [],
            "source": source,
            "read": read,
            "timestamp": timestamp
        }
    return None


@app.post("/note/mark_read", response_model=dict)
async def mark_note_read(req: Request):
    data = await req.json()
    note_id = data.get("id")
    if note_id is not None:
        db.mark_note_as_read(note_id)
        return {"result": "ok"}
    return {"error": "missing note id"}


@app.post("/note/set_tags", response_model=dict)
async def set_note_tags(req: Request):
    data = await req.json()
    note_id = data.get("id")
    tags = data.get("tags", [])
    if note_id is not None:
        db.set_tags(note_id, tags)
        return {"result": "ok"}
    return {"error": "missing note id"}


@app.get("/note/random", response_model=Optional[NoteOutput])
def get_random_note_by_tags(tags: Optional[List[str]] = None):
    note = db.get_random_note_by_tags(tags or [])
    if note:
        note_id, text, note_tags, source, read, timestamp = note
        return {
            "id": note_id,
            "text": text,
            "tags": note_tags.split(",") if note_tags else [],
            "source": source,
            "read": read,
            "timestamp": timestamp
        }
    return None


@app.get("/note/by_tag", response_model=List[NoteOutput])
def get_notes_by_tag(tag: str):
    all_notes = db.read_notes(limit=1000)
    return [
        {
            "id": note[0],
            "text": note[1],
            "tags": note[2].split(",") if note[2] else [],
            "source": note[3],
            "read": note[4],
            "timestamp": note[5]
        }
        for note in all_notes if tag in (note[2].split(",") if note[2] else [])
    ]


@app.on_event("shutdown")
def shutdown():
    db.close()
