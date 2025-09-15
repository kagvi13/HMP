---
title: HyperCortex Mesh Protocol — JSON Schemas
description: This directory contains JSON Schema definitions for the core data models
  used in the HyperCortex Mesh Protocol (HMP).   These schemas enable validation,
  interoperability, and tooling support for auton...
type: Article
tags:
- Mesh
- Agent
- JSON
- HMP
---

# HyperCortex Mesh Protocol — JSON Schemas

This directory contains JSON Schema definitions for the core data models used in the HyperCortex Mesh Protocol (HMP).  
These schemas enable validation, interoperability, and tooling support for autonomous agents.

| Data Model / Object        | File / Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------------|
| Concept                    | [concept.json](concept.json) — Semantic knowledge unit               |
| CognitiveDiaryEntry        | [diary_entry.json](diary_entry.json) — Agent's reasoning log entry   |
| Goal                       | [goal.json](goal.json) — Shared objective pursued collaboratively    |
| Task                       | [task.json](task.json) — Actionable unit contributing to a goal       |
| ConsensusVote              | [vote.json](vote.json) — Vote in a Mesh consensus process             |
| ReputationProfile          | [reputation.json](reputation.json) — Tracks agent trust and contribution metrics |
| DHT Protocol               | [dht_protocol.json](dht_protocol.json) — Recommendations for peer discovery & exchange |
| Message (P2P)              | [message_p2p.json](message_p2p.json) — Direct point-to-point message |
| Message (Broadcast)        | [message_broadcast.json](message_broadcast.json) — Broadcast messages |
| Message (Relay / Mailman)  | [message_relay.json](message_relay.json) — Relay / Mailman messages  |
| Message (Topiccast)        | [message_topiccast.json](message_topiccast.json) — Topic-based messages |


---
> ⚡ [AI friendly version docs (structured_md)](../../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol — JSON Schemas",
  "description": "# HyperCortex Mesh Protocol — JSON Schemas  This directory contains JSON Schema definitions for the ..."
}
```
