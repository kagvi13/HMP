# agents/mcp_server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask, request, jsonify
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import GraphExport 
from storage import Storage
from tools.concept_store import ConceptStore
from tools.notebook_store import NotebookStore
import random

app = FastAPI(title="HMP MCP-Agent API", version="0.1")

# Добавляем CORS (полезно, если API вызывается с веб-клиента)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можем позже ограничить, если потребуется
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация хранилищ
concept_store = ConceptStore()
notebook_store = NotebookStore()
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

class Node(BaseModel):
    id: str
    label: str
    tags: List[str] = []

class Edge(BaseModel):
    source: str
    target: str
    relation: str

class GraphImportData(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []

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

class ConceptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

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
    return {"message": "HMP MCP-Agent API is running"}

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
    return concept_store.export_as_json()

@app.put("/update_concept/{concept_id}")
def update_concept(concept_id: int, update: ConceptUpdate):
    db.update_concept(concept_id, update.name, update.description)
    return {"result": f"concept {concept_id} updated"}

@app.get("/tag_stats", response_model=dict)
def tag_stats():
    return db.get_tag_stats()

@app.get("/search_links", response_model=List[LinkExport])
def search_links(relation: str):
    rows = db.search_links_by_relation(relation)
    return [
        {
            "id": row[0],
            "source_id": row[1],
            "target_id": row[2],
            "relation": row[3]
        }
        for row in rows
    ]

@app.get("/search_concepts", response_model=List[Concept])
def search_concepts(query: str):
    results = db.search_concepts(query)
    return [
        {"concept_id": row[0], "name": row[1], "description": row[2]}
        for row in results
    ]

@app.post("/merge_concepts", response_model=dict)
def merge_concepts(source_id: int, target_id: int):
    db.merge_concepts(source_id, target_id)
    return {"result": f"concept {source_id} merged into {target_id}"}

@app.post("/relate_concepts", response_model=LinkOutput)
def relate_concepts(source_name: str, target_name: str, relation: str):
    sid = db.find_concept_id_by_name(source_name)
    tid = db.find_concept_id_by_name(target_name)
    if sid is None or tid is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    link_id = db.add_link(sid, tid, relation)
    return {"link_id": link_id}

@app.get("/tag_cloud", response_model=dict)
def tag_cloud():
    return db.get_tag_stats()

@app.get("/get_concept/{concept_id}")
def get_concept(concept_id: str):
    concept = concept_store.get(concept_id)
    if concept:
        return concept
    raise HTTPException(status_code=404, detail="Concept not found")

@app.get("/get_entry/{entry_id}")
def get_entry(entry_id: str):
    entry = notebook_store.get(entry_id)
    if entry:
        return entry
    raise HTTPException(status_code=404, detail="Entry not found")

@app.post("/search_entries")
def search_entries(query: str):
    results = notebook_store.search(query)
    return results

@app.post("/import_graph")
def import_graph(graph_data: GraphImportData):
    concept_store.import_from_json(graph_data.dict())
    print(f"[INFO] Imported {len(graph_data.nodes)} nodes, {len(graph_data.edges)} edges")
    return {"status": "ok"}

# === Notebook API ===

@app.post("/notebook/add")
async def add_note(req: Request):
    data = await req.json()
    text = data.get("text", "").strip()
    if not text:
        return {"status": "error", "message": "Empty text"}
    notebook.add_note(text, source="user")
    return {"status": "ok", "message": "Note added"}

@app.get("/notebook/next")
def get_next_note():
    note = notebook.get_first_unread_note()
    if note:
        note_id, text, source, timestamp, tags = note
        return {
            "id": note_id,
            "text": text,
            "source": source,
            "timestamp": timestamp,
            "tags": tags
        }
    return {"status": "empty", "message": "No unread notes"}

@app.post("/notebook/mark_read")
async def mark_note_read(req: Request):
    data = await req.json()
    note_id = data.get("id")
    if note_id is not None:
        notebook.mark_note_as_read(note_id)
        return {"status": "ok"}
    return {"status": "error", "message": "Missing note id"}

# === ✨ Дополнительные эндпоинты для заметок ===

@app.route("/notes/latest", methods=["GET"])
def get_latest_notes():
    """Вернуть последние N заметок (по умолчанию 10)."""
    count = int(request.args.get("count", 10))
    notes = storage.diary[-count:]
    return jsonify([note.to_dict() for note in notes])

@app.route("/notes/random", methods=["GET"])
def get_random_note():
    """Вернуть случайную заметку из дневника."""
    if not storage.diary:
        return jsonify({})
    note = random.choice(storage.diary)
    return jsonify(note.to_dict())

@app.route("/notes/set_tags", methods=["POST"])
def set_tags():
    """Обновить теги у заметки по ID."""
    data = request.json
    note_id = data.get("id")
    tags = data.get("tags", [])
    for note in storage.diary:
        if note.id == note_id:
            note.tags = tags
            return jsonify({"status": "ok"})
    return jsonify({"error": "not found"}), 404

@app.route("/notes/by_tag", methods=["GET"])
def get_notes_by_tag():
    tag = request.args.get("tag")
    result = [note.to_dict() for note in storage.diary if tag in note.tags]
    return jsonify(result)

# === Run === 
if __name__ == "__main__":
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8080, reload=True)

# === Shutdown ===

@app.on_event("shutdown")
def shutdown():
    db.close()
