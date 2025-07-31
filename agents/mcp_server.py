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

class ConceptInput(BaseModel):
    name: str
    description: Optional[str] = ""

class ConceptOutput(BaseModel):
    concept_id: int

class Concept(BaseModel):
    concept_id: int
    name: str
    description: Optional[str]

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

class GraphExport(BaseModel):
    nodes: List[Concept]
    edges: List[Edge]

class GraphImportData(BaseModel):
    nodes: List[Concept]
    edges: List[Edge]

class ConceptUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

class ConceptQueryOutput(BaseModel):
    matches: List[Concept]

class NoteTagUpdate(BaseModel):
    id: int
    tags: List[str] = []

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

@app.get("/diary/get_entry/{entry_id}", response_model=DiaryOutput)
def get_diary_entry(entry_id: int):
    row = db.get_diary_entry(entry_id)
    if row:
        return {
            "id": row[0],
            "text": row[1],
            "tags": row[2].split(",") if row[2] else [],
            "timestamp": row[3]
        }
    raise HTTPException(status_code=404, detail="Entry not found")

@app.post("/diary/search_entries", response_model=DiaryListOutput)
def search_entries(query: str):
    rows = db.search_diary_entries(query)
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

@app.get("/diary/tag_stats", response_model=dict)
def tag_stats():
    return db.get_tag_stats()

@app.get("/diary/export", response_model=DiaryListOutput)
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

@app.post("/graph/add_concept", response_model=ConceptOutput)
def add_concept(concept: ConceptInput):
    cid = db.add_concept(concept.name, concept.description)
    return {"concept_id": cid}

@app.post("/graph/add_link", response_model=LinkOutput)
def add_link(link: LinkInput):
    link_id = db.add_link(link.source_id, link.target_id, link.relation)
    return {"link_id": link_id}

@app.get("/graph/expand", response_model=GraphExpansionOutput)
def expand_graph(start_id: int, depth: int = 1):
    links = db.expand_concept_graph(start_id, depth)
    return {"links": links}

@app.get("/graph/list_concepts", response_model=List[Concept])
def list_concepts():
    rows = db.list_concepts()
    return [
        {"concept_id": r[0], "name": r[1], "description": r[2]}
        for r in rows
    ]

@app.get("/graph/list_links", response_model=List[Edge])
def list_links():
    return db.list_links()

@app.get("/graph/get_concept/{id}", response_model=Concept)
def get_concept(id: int):
    concept = db.get_concept(id)
    if concept:
        return {"concept_id": concept[0], "name": concept[1], "description": concept[2]}
    raise HTTPException(status_code=404, detail="Concept not found")

@app.delete("/graph/delete_concept/{id}")
def delete_concept(id: int):
    db.delete_concept(id)
    return {"result": f"concept {id} deleted"}

@app.delete("/graph/delete_link/{id}")
def delete_link(id: int):
    db.delete_link(id)
    return {"result": f"link {id} deleted"}

@app.put("/graph/update_concept/{id}")
def update_concept(id: int, update: ConceptUpdate):
    db.update_concept(id, update.name, update.description)
    return {"result": f"concept {id} updated"}

@app.post("/graph/merge_concepts")
def merge_concepts(source_id: int, target_id: int):
    db.merge_concepts(source_id, target_id)
    return {"result": f"concept {source_id} merged into {target_id}"}

@app.get("/graph/search_links", response_model=List[Edge])
def search_links(relation: str):
    return db.search_links_by_relation(relation)

@app.get("/graph/search_concepts", response_model=List[Concept])
def search_concepts(query: str):
    rows = db.search_concepts(query)
    return [{"concept_id": r[0], "name": r[1], "description": r[2]} for r in rows]

@app.get("/graph/query_concept", response_model=ConceptQueryOutput)
def query_concept(name: str):
    rows = db.query_concept(name)
    return {
        "matches": [
            {"concept_id": r[0], "name": r[1], "description": r[2]}
            for r in rows
        ]
    }

@app.post("/graph/relate_concepts", response_model=LinkOutput)
def relate_concepts(source_name: str, target_name: str, relation: str):
    sid = db.get_concept_id_by_name(source_name)
    tid = db.get_concept_id_by_name(target_name)
    if sid is None or tid is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    link_id = db.add_link(sid, tid, relation)
    return {"link_id": link_id}

@app.get("/graph/export", response_model=GraphExport)
def export_graph():
    return db.export_graph()

@app.post("/graph/import")
def import_graph(graph_data: GraphImportData):
    db.import_graph(graph_data)
    return {"status": "ok"}

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
def mark_note_read(data: NoteTagUpdate):
    db.mark_note_as_read(data.id)
    return {"result": "ok"}

@app.post("/note/set_tags", response_model=dict)
def set_note_tags(data: NoteTagUpdate):
    db.set_tags(data.id, data.tags)
    return {"result": "ok"}

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
