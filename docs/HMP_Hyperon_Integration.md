## 🤝 Integration Plan: HMP ↔ OpenCog Hyperon

### 🔍 Goal

Enable interoperability between the **HyperCortex Mesh Protocol (HMP)** and **OpenCog Hyperon** to allow:

* Bi-directional semantic graph sync (HMP JSON ⇄ AtomSpace)
* Ethical filtering of cognitive operations (via EGP)
* Cognitive diary translation for symbolic reasoning
* Mesh-wide participation of Hyperon agents in consensus and alignment tasks

---

### 🧠 Architecture Overview

#### Components:

* **HMP Server**: Serves JSON-graph data, BitTorrent sync, EGP filtering
* **MCP Server**: Optional middleware for advanced coordination (agent meta-control)
* **Hyperon Node**: Local instance with AtomSpace, PLN, MOSES

#### Flow:

```
[HMP Agent] ⇄ [HMP Server/API] ⇄ [Mapping Layer] ⇄ [Hyperon AtomSpace]
                               ↕                ↕
                           [EGP Validator]   [MeTTa Rewriter (optional)]
```

---

### 🔄 Mapping Data Structures

#### HMP JSON → AtomSpace:

| HMP Element       | Atom Type     | Notes                      |
| ----------------- | ------------- | -------------------------- |
| `concept.id`      | ConceptNode   | Unique ID for node         |
| `concept.label`   | PredicateNode | Associated label           |
| `relation.source` | ConceptNode   | Source of relation         |
| `relation.target` | ConceptNode   | Target of relation         |
| `relation.type`   | PredicateNode | Type of edge               |
| `goal.intent`     | GoalNode      | Used in cognitive planning |
| `task.action`     | ExecutionLink | Potential trigger in MOSES |

> Additional mappings may be derived from `semantic_repo.json` specs.

---

### 🧪 Test Scenarios

#### Integration Benchmarks:

* ✅ Load 100 HMP concepts → AtomSpace with ≥95% accuracy
* ✅ Export 50 AtomSpace nodes → HMP JSON (preserving intent + labels)
* ✅ Apply EGP filters: ≥95% rejection of unethical goal/task constructs
* ✅ Perform reasoning via PLN on HMP-imported graph
* ✅ Validate BitTorrent-based graph sync for distributed setups

---

### 🧩 Implementation Tasks

#### Phase 1: Minimal Working Prototype (Jul–Sep 2025)

* [ ] Implement HMP-to-AtomSpace mapper (Python)
* [ ] Docker Compose: HMP Server + Hyperon Node + Bridge Layer
* [ ] Add `EGPValidator` Python module for applying ethical rules
* [ ] Quick Start demo: sync, filter, reason with HMP-0003 examples

#### Phase 2: Cognitive Diary & MeTTa Layer (Q4 2025)

* [ ] Parse diary entries → MeTTa patterns
* [ ] Implement MeTTa → HMP rewrites for CogSync
* [ ] Jupyter Notebook: interactive EGP inspection and AtomSpace queries

#### Phase 3: Full CogSync Interop & MCP Compatibility (2026)

* [ ] Extend mapping to cognitive timelines (timestamped thoughts)
* [ ] Enable cross-agent reasoning: Hyperon + HMP + Grok-style agents
* [ ] EGP → PLN export rules (pluggable ethical knowledge base)

---

### 📚 Audit Context

This integration plan fulfills multiple requests from `HMP-0003-consolidated_audit.md`, including:

* **Section 1:** CogSync interop with external agents
* **Section 2:** EGP enforcement across symbolic backends
* **Section 14.5:** Mesh ↔ external networks integration guidelines
* **Section 7:** Improve onboarding examples in Quick Start docs

---

### 📌 Notes

* AtomSpace supports efficient querying, so JSON → AtomSpace mapping should preserve logical semantics.
* EGP filters should work as composable modules before inserting into AtomSpace.
* BitTorrent `magnet:` links can serve as transport layer for semantic deltas.
