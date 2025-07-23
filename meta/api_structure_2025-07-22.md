API structure, 2025-07-22

# agents/mcp_server.py

## === Модели запроса/ответа ===

- class EntryInput(BaseModel):
- class EntryOutput(BaseModel):
- class EntryListOutput(BaseModel):
- class ConceptInput(BaseModel):
- class ConceptOutput(BaseModel):
- class LinkInput(BaseModel):
- class LinkOutput(BaseModel):
- class Node(BaseModel):
- class Edge(BaseModel):
- class GraphImportData(BaseModel):
- class GraphExpansionOutput(BaseModel):
- class Concept(BaseModel):
- class ConceptQueryOutput(BaseModel):
- class DiaryEntry(BaseModel):
- class DiaryExport(BaseModel):
- class ConceptExport(BaseModel):
- class LinkExport(BaseModel):
- class GraphExport(BaseModel):
- class ConceptUpdate(BaseModel):

## === Эндпойнты ===

- @app.get("/status")
- @app.post("/write_entry", response_model=dict)
- @app.get("/read_entries", response_model=EntryListOutput)
- @app.get("/")
- @app.post("/add_concept", response_model=ConceptOutput)
- @app.post("/add_link", response_model=LinkOutput)
- @app.get("/expand_graph", response_model=GraphExpansionOutput)
- @app.get("/query_concept", response_model=ConceptQueryOutput)
- @app.get("/list_concepts", response_model=List[Concept])
- @app.get("/list_links", response_model=List[Edge])
- @app.delete("/delete_concept/{concept_id}")
- @app.delete("/delete_link/{link_id}")
- @app.delete("/delete_entry/{entry_id}")
- @app.get("/export_diary", response_model=DiaryExport)
- @app.get("/export_graph", response_model=GraphExport)
- @app.put("/update_concept/{concept_id}")
- @app.get("/tag_stats", response_model=dict)
- @app.get("/search_links", response_model=List[LinkExport])
- @app.get("/search_concepts", response_model=List[Concept])
- @app.post("/merge_concepts", response_model=dict)
- @app.post("/relate_concepts", response_model=LinkOutput)
- @app.get("/tag_cloud", response_model=dict)
- @app.get("/get_concept/{concept_id}")
- @app.get("/get_entry/{entry_id}")
- @app.post("/search_entries")
- @app.post("/import_graph")
- @app.post("/notebook/add")
- @app.get("/notebook/next")
- @app.post("/notebook/mark_read")
- @app.route("/notes/latest", methods=["GET"])
- @app.route("/notes/random", methods=["GET"])
- @app.route("/notes/set_tags", methods=["POST"])
- @app.route("/notes/by_tag", methods=["GET"])
- @app.on_event("shutdown")

# agents/storage.py

- class Storage:
  - def __init__(self, config=None):
  - def _init_db(self):
  - def write_entry(self, text, tags=None):
  - def read_entries(self, limit=10, tag_filter=None):
  - def search_entries_by_time(self, from_ts, to_ts):
  - def add_concept(self, name, description=None):
  - def query_concept(self, name_substr):
  - def add_link(self, source_id, target_id, relation):
  - def list_concepts(self):
  - def list_links(self):
  - def expand_graph(self, start_id, depth):
  - def delete_concept(self, concept_id):
  - def delete_link(self, link_id):
  - def delete_entry(self, entry_id):
  - def export_diary(self):
  - def export_graph(self):
  - def update_concept(self, concept_id, name=None, description=None):
  - def get_tag_stats(self):
  - def search_links_by_relation(self, relation):
  - def search_concepts(self, query):
  - def merge_concepts(self, source_id, target_id):
  - def find_concept_id_by_name(self, name):
  - def close(self):

# tools/concept_store.py

- class Concept:
  - def __init__(self, id: Optional[str] = None, label: str = "", description: str = "", tags: Optional[List[str]] = None)
  - def to_dict(self):
  - @staticmethod
  - def from_dict(data):

- class Edge:
  - def __init__(self, source: str, target: str, relation: str = "related_to"):
  - def to_dict(self):
  - @staticmethod
  - def from_dict(data):

- class ConceptStore:
  - def __init__(self):
  - def add(self, concept: Concept):
  - def get(self, concept_id: str) -> Optional[dict]:
  - def add_edge(self, edge: Edge):
  - def find_by_label(self, label: str) -> Optional[Concept]:
  - def import_from_json(self, data: dict) -> dict:
  - def export_as_json(self) -> GraphExport:
  - def all_concepts(self):
  - def all_edges(self):
  - def remove_concept(self, concept_id: str):
  - def remove_edge(self, source_id: str, target_id: str, relation: str):
  - def debug_print(self):

# agents/tools/notebook_store.py

- class Notebook:
  - def __init__(self, db_path=DB_FILE):
  - def _init_db(self):
  - def add_note(self, text, source="user"):
  - def get_latest_notes(self, limit=10):
  - def get_notes_after(self, since_ts):
  - def get_first_unread_note(self):
  - def mark_note_as_read(self, note_id: int):
  - def set_tags(self, note_id: int, tags: list[str]):
  - def get_random_note_by_tags(self, include_tags: list[str]):
  - def close(self):
