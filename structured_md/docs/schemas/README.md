---
title: JSON Schemas and Examples for HyperCortex Mesh Protocol (HMP)
description: This directory contains **JSON Schema definitions** for the core data
  models used in the HyperCortex Mesh Protocol (HMP).   These schemas enable validation,
  interoperability, and tooling support for a...
type: Article
tags:
- Agent
- JSON
- HMP
- Mesh
---

# JSON Schemas and Examples for HyperCortex Mesh Protocol (HMP)

This directory contains **JSON Schema definitions** for the core data models used in the HyperCortex Mesh Protocol (HMP).  
These schemas enable validation, interoperability, and tooling support for autonomous agents.

- `*.json` files — JSON Schema definitions for validation  
- `examples/*.json` — ready-to-use example objects demonstrating valid instances of each model  

| Data Model / Object        | File / Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------------|
| Concept                    | [concept.json](concept.json) — Semantic knowledge unit. |
| CognitiveDiaryEntry        | [diary_entry.json](diary_entry.json) — Agent's reasoning log entry. |
| Goal                       | [goal.json](goal.json) — Shared objective pursued collaboratively. |
| Task                       | [task.json](task.json) — Actionable unit contributing to a goal. |
| ConsensusVote              | [vote.json](vote.json) — Vote in a Mesh consensus process. |
| ReputationProfile          | [reputation.json](reputation.json) — Tracks agent trust and contribution metrics. |
| DHT Protocol               | [dht_protocol.json](dht_protocol.json) — Recommendations for peer discovery & exchange. |
| Message                     | [message.json](message.json) — Base schema for all message types. |

> All ready-to-use example objects can be found in the [`examples/`](examples/) folder.

---
> ⚡ [AI friendly version docs (structured_md)](../../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "JSON Schemas and Examples for HyperCortex Mesh Protocol (HMP)",
  "description": "# JSON Schemas and Examples for HyperCortex Mesh Protocol (HMP)  This directory contains **JSON Sche..."
}
```
