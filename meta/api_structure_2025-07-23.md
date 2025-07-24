API structure, 2025-07-23

# agents/mcp_server.py

**MODELS**
- class NoteInput(BaseModel):
- class NoteOutput(BaseModel):
- class DiaryInput(BaseModel):
- class DiaryOutput(BaseModel):
- class DiaryListOutput(BaseModel):
- class ConceptInput(BaseModel):
- class ConceptOutput(BaseModel):
- class Concept(BaseModel):
- class LinkInput(BaseModel):
- class LinkOutput(BaseModel):
- class Edge(BaseModel):
- class GraphExpansionOutput(BaseModel):
- class GraphExport(BaseModel):
- class GraphImportData(BaseModel):
- class ConceptUpdate(BaseModel):
- class ConceptQueryOutput(BaseModel):
- class NoteTagUpdate(BaseModel):
**ROUTES**
- @app.get("/status")
- @app.post("/diary/write", response_model=dict)
- @app.get("/diary/read", response_model=DiaryListOutput)
- @app.delete("/diary/delete/{entry_id}")
- @app.get("/diary/get_entry/{entry_id}", response_model=DiaryOutput)
- @app.post("/diary/search_entries", response_model=DiaryListOutput)
- @app.get("/diary/tag_stats", response_model=dict)
- @app.get("/diary/export", response_model=DiaryListOutput)
- @app.post("/graph/add_concept", response_model=ConceptOutput)
- @app.post("/graph/add_link", response_model=LinkOutput)
- @app.get("/graph/expand", response_model=GraphExpansionOutput)
- @app.get("/graph/list_concepts", response_model=List[Concept])
- @app.get("/graph/list_links", response_model=List[Edge])
- @app.get("/graph/get_concept/{id}", response_model=Concept)
- @app.delete("/graph/delete_concept/{id}")
- @app.delete("/graph/delete_link/{id}")
- @app.put("/graph/update_concept/{id}")
- @app.post("/graph/merge_concepts")
- @app.get("/graph/search_links", response_model=List[Edge])
- @app.get("/graph/search_concepts", response_model=List[Concept])
- @app.get("/graph/query_concept", response_model=ConceptQueryOutput)
- @app.post("/graph/relate_concepts", response_model=LinkOutput)
- @app.get("/graph/export", response_model=GraphExport)
- @app.post("/graph/import")
- @app.post("/note/write", response_model=dict)
- @app.get("/note/next", response_model=Optional[NoteOutput])
- @app.post("/note/mark_read", response_model=dict)
- @app.post("/note/set_tags", response_model=dict)
- @app.get("/note/random", response_model=Optional[NoteOutput])
- @app.get("/note/by_tag", response_model=List[NoteOutput])
- @app.on_event("shutdown")

# agents/tools/storage.py

- class Storage:
  - def __init__(self, config=None):
  - def _init_db(self):
  - **Методы для работы с дневником**
    - def write_diary_entry(self, text, tags=None):
    - def read_diary_entries(self, limit=10, tag_filter=None):
    - def search_diary_by_time_range(self, from_ts, to_ts):
    - def delete_diary_entry_by_id(self, entry_id):
    - def get_diary_tag_stats(self):
    - def export_diary_entries(self):
  - **Методы для работы с концептами**
    - def create_concept(self, name, description=None):
    - def get_concept_by_name(self, name):
    - def list_concepts(self):
  - **Методы для работы с связями**
    - def link_concepts(self, from_name, to_name, relation_type):
    - def get_links_for_concept(self, concept_name):
  - **Сложные операции над графом**
    - def expand_concept_graph(self, start_id, depth):
    - def delete_concept_by_id(self, concept_id):
    - def delete_link_by_id(self, link_id):
    - def export_semantic_graph(self):
    - def update_concept_fields(self, concept_id, name=None, description=None):
    - def search_links_by_relation(self, relation):
    - def search_concepts(self, query):
    - def merge_concepts(self, source_id, target_id):
    - def find_concept_id_by_name(self, name):
  - **Методы для заметок**
    - def write_note(self, text, tags=None):
    - def read_notes(self, limit=10, tag_filter=None):
    - def get_notes_after(self, since_ts):
    - def get_first_unread_note(self):
    - def mark_note_as_read(self, note_id: int):
    - def set_tags(self, note_id: int, tags: list[str]):
    - def get_random_note_by_tags(self, include_tags: list[str]):

  - **Утилиты**
    - def close(self):

