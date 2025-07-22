# tools/concept_store.py

import uuid
from typing import Dict, List, Optional

class Concept:
    def __init__(self, id: Optional[str] = None, label: str = "", description: str = "", tags: List[str] = []):
        self.id = id or str(uuid.uuid4())
        self.label = label
        self.description = description
        self.tags = tags

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "tags": self.tags
        }

    @staticmethod
    def from_dict(data):
        return Concept(
            id=data.get("id"),
            label=data.get("label", ""),
            description=data.get("description", ""),
            tags=data.get("tags", [])
        )

class Edge:
    def __init__(self, source: str, target: str, relation: str = "related_to"):
        self.source = source
        self.target = target
        self.relation = relation

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation
        }

    @staticmethod
    def from_dict(data):
        return Edge(
            source=data["source"],
            target=data["target"],
            relation=data.get("relation", "related_to")
        )


class ConceptStore:
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.edges: List[Edge] = []

    def add(self, concept: Concept):
        self.concepts[concept.id] = concept

    def get(self, concept_id: str) -> Optional[dict]:
        concept = self.concepts.get(concept_id)
        return concept.to_dict() if concept else None

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def import_from_json(self, data: dict):
        for c in data.get("nodes", []):
            concept = Concept.from_dict(c)
            self.add(concept)
        for e in data.get("edges", []):
            edge = Edge.from_dict(e)
            self.add_edge(edge)

    def export_as_json(self):
        return {
            "nodes": [c.to_dict() for c in self.concepts.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

    def all_concepts(self):
        return [c.to_dict() for c in self.concepts.values()]

    def all_edges(self):
        return [e.to_dict() for e in self.edges]
