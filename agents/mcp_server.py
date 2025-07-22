# agents/mcp_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from storage import Storage

app = FastAPI(title="HMP MCP-Agent API", version="0.1")

db = Storage()

# === Модели запроса/ответа ===

class EntryInput(BaseModel):
    text: str
    tags: Optional[List[str]] = []
    timestamp: Optional[str] = None

class EntryOutput(BaseModel):
    id: int
    text: str
    tags: List[str]
    timestamp: str

class EntryListOutput(BaseModel):
    entries: List[EntryOutput]

# === Эндпойнты ===

@app.get("/status")
def status():
    return {
        "status": "ok",
        "agent": "HMP-MCP",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/write_entry", response_model=dict)
def write_entry(entry: EntryInput):
    db.write_entry(entry.text, entry.tags)
    return {"result": "entry saved"}

@app.get("/read_entries", response_model=EntryListOutput)
def read_entries(limit: int = 5, tag: Optional[str] = None):
    raw = db.read_entries(limit=limit, tag_filter=tag)
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

@app.get("/")
def root():
    return {"message": "Welcome to HMP MCP-Agent API"}

# === Shutdown ===

@app.on_event("shutdown")
def shutdown():
    db.close()
