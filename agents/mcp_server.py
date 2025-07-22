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

class ConceptInput(BaseModel):
    name: str
    description: Optional[str] = None

class ConceptOutput(BaseModel):
    concept_id: int

class LinkInput(BaseModel):
    source_id: int
    target_id: int
    relation: str

class LinkOutput(BaseModel):
    link_id: int

class Edge(BaseModel):
    source_id: int
    target_id: int
    relation: str

class GraphExpansionOutput(BaseModel):
    links: List[Edge]

class Concept(BaseModel):
    concept_id: int
    name: str
    description: Optional[str] = None

class ConceptQueryOutput(BaseModel):
    matches: List[Concept]

class DiaryEntry(BaseModel):
    id: int
    text: str
    tags: List[str]
    timestamp: str

class DiaryExport(BaseModel):
    entries: List[DiaryEntry]

class ConceptExport(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class LinkExport(BaseModel):
    id: int
    source_id: int
    target_id: int
    relation: str

class GraphExport(BaseModel):
    concepts: List[ConceptExport]
    links: List[LinkExport]

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

@app.post("/add_concept", response_model=ConceptOutput)
def add_concept(concept: ConceptInput):
    cid = db.add_concept(concept.name, concept.description)
    return {"concept_id": cid}

@app.post("/add_link", response_model=LinkOutput)
def add_link(link: LinkInput):
    link_id = db.add_link(link.source_id, link.target_id, link.relation)
    return {"link_id": link_id}

@app.get("/expand_graph", response_model=GraphExpansionOutput)
def expand_graph(start_id: int, depth: int = 1):
    raw_links = db.expand_graph(start_id, depth)
    edges = [{"source_id": s, "target_id": t, "relation": r} for s, t, r in raw_links]
    return {"links": edges}

@app.get("/query_concept", response_model=ConceptQueryOutput)
def query_concept(name: str):
    results = db.query_concept(name)
    return {
        "matches": [
            {"concept_id": row[0], "name": row[1], "description": row[2]}
            for row in results
        ]
    }

@app.get("/list_concepts", response_model=List[Concept])
def list_concepts():
    rows = db.list_concepts()
    return [
        {"concept_id": row[0], "name": row[1], "description": row[2]}
        for row in rows
    ]

@app.get("/list_links", response_model=List[Edge])
def list_links():
    rows = db.list_links()
    return [
        {"source_id": row[1], "target_id": row[2], "relation": row[3]}
        for row in rows
    ]

@app.delete("/delete_concept/{concept_id}")
def delete_concept(concept_id: int):
    db.delete_concept(concept_id)
    return {"result": f"concept {concept_id} deleted"}

@app.delete("/delete_link/{link_id}")
def delete_link(link_id: int):
    db.delete_link(link_id)
    return {"result": f"link {link_id} deleted"}

@app.delete("/delete_entry/{entry_id}")
def delete_entry(entry_id: int):
    db.delete_entry(entry_id)
    return {"result": f"entry {entry_id} deleted"}

@app.get("/export_diary", response_model=DiaryExport)
def export_diary():
    rows = db.export_diary()
    return {
        "entries": [
            {
                "id": r[0],
                "text": r[1],
                "tags": r[2].split(",") if r[2] else [],
                "timestamp": r[3]
            }
            for r in rows
        ]
    }

@app.get("/export_graph", response_model=GraphExport)
def export_graph():
    data = db.export_graph()
    concepts = [
        {"id": c[0], "name": c[1], "description": c[2]} for c in data["concepts"]
    ]
    links = [
        {"id": l[0], "source_id": l[1], "target_id": l[2], "relation": l[3]} for l in data["links"]
    ]
    return {"concepts": concepts, "links": links}

# === Shutdown ===

@app.on_event("shutdown")
def shutdown():
    db.close()
