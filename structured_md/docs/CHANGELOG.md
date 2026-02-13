---
title: HyperCortex Mesh Protocol — Changelog
description: '## HMP-0005 (October 2025) — Core Specification v5.0  **Architecture:**
  * Formalized immutable container model with explicit proof chains. * Unified cognitive,
  container, and network layers into a sin...'
type: Article
tags:
- CogSync
- MeshConsensus
- EGP
- JSON
- Ethics
- Mesh
- Agent
- HMP
- GMP
- Scenarios
---

# HyperCortex Mesh Protocol — Changelog

## HMP-0005 (October 2025) — Core Specification v5.0

**Architecture:**
* Formalized immutable container model with explicit proof chains.
* Unified cognitive, container, and network layers into a single protocol stack.
* Introduced canonical container header and semantic `related.*` references.

**Security & Verification:**
* Standardized canonical JSON, hashing, and Ed25519 signatures.
* Defined encrypted + compressed container format.
* Enabled verification without payload decryption.

**Consensus & Reasoning:**
* Introduced formal `vote` and `consensus_result` containers.
* Enabled forked and parallel consensus results.
* Defined reproducible aggregation via explicit dependency references.

**Networking:**
* Integrated DHT-based discovery as a first-class layer.
* Defined TTL, propagation scope, and routing semantics.

**Extensibility:**
* Added Future Extensions framework (groups, reputation, streaming, bridges).
* Defined protocol evolution rules for the 5.x series.

This version supersedes all RFC-based HMP 4.x specifications.

## HMP-0004 (July 2025) — RFC Version 4.1

**Protocols:**
* **Added `5.8 Message Routing & Delivery` section** — including direct, broadcast, relay, and topic messaging modes.

**Data Models:**
* **Defined `6.5.8 Message Object Schema`** — standard JSON format for inter-agent communication.

**Cognitive Workflows:**
* **Added `7.9 Message Handling & Delivery Workflows`** — describing message processing, relay behavior, and routing.

## HMP-0004 (July 2025) — RFC Version 4.0

**Major Changes**
* Introduced new sections: *Cognitive Workflows*, *Agent Roles*, *Governance*, *Compression*, and *Simulation*.
* Added experimental APIs: *Consent Request*, *Explainability*, *Voice Interface*.
* Expanded *Quick Start Guide* and updated *Example Use Cases* with new flows and APIs.
* Integrated BitTorrent/IPFS snapshot syncing, pseudonymous voting, and ethical filters.

**Protocol and Architecture Updates**
* Enhanced *CogSync* with chunked syncing, selective edge sync, and experimental Dat/IPFS support.
* Refined *MeshConsensus* with adaptive models and EGP-integrated filters.
* Extended *EGP* with principle hierarchy, local norm integration, and modular ethics ontologies.
* Improved fallback and handshake logic across all protocols.

**Data Model Improvements**
* Added new objects: `CogDiarySnapshot`, `SnapshotIndex`, `EthicalConflict`.
* Introduced *Reputation Ontology Extension* and support for multi-format schema negotiation (JSON/YAML/Protobuf).
* Unified schema structure, examples, and versioning across `6.2` and `6.5`.

**Cognitive Layer Enhancements**
* Formalized cognitive workflows for reflection, delegation, and hypothesis validation.
* Refined semantic change tracking and diary summarization processes.
* Defined agent self-assessment and meta-reflection protocols.

**Trust & Security Enhancements**
* Added *Snapshot Security*: DID-signatures, ZKP verification, and trusted seeders.
* Extended *Sybil resistance*, post-quantum key support, and anonymized voting mechanisms.
* Improved trust-based access control and event auditability.

**Interoperability & Event Integration**
* Added *Event-Driven Architecture* and format negotiation layer.
* Documented integration patterns for REST, gRPC, MQTT, and message brokers.
* Clarified cross-protocol participation (e.g. Hyperon, TreeQuest, AutoGPT).

**Testing & Simulation**
* New Appendix C with *Ethical Stress Suite*, snapshot sync simulation, and open test datasets.
* Introduced *Agent-on-Agent Dialog Simulation* for consent learning and negotiation modeling.

**Future Directions**
* Extended roadmap with *Snapshot Markets*, *Meta-Protocol Proposals*, and *Multi-Agent Training Environments*.
* Prototype tools proposed: *MeshGit*, *CogForge*, and *HyperCortex Forge* for cognitive source control and collaborative evolution.

## HMP-0003 (July 2025) — RFC Version 3.0

**Major Changes**
* Rewritten and expanded full RFC document structure.
* Added Quick Start Guide with demo commands and cross-protocol notes.
* Introduced a detailed Deployment Scenarios section describing Core, Edge, IoT, and Hybrid environments.
* Created the Interoperability with External Systems section (API Gateway, Event-driven integrations, Auth).
* Extended Future Roadmap with Federated Meta-Learning, Quantum Mesh, Multi-Protocol Nodes, DAO integration, and Cognitive Source Control.
* Enhanced clarity and modularity across all sections for easier reference and further evolution.

**Protocol and Architecture Updates**
* Refined protocol descriptions for CogSync, MeshConsensus, GMP, EGP, and NDP.
* Improved fallback scenarios, error handling, and adaptive consensus algorithms.
* Detailed internal/external agent interactions and cross-mesh collaboration patterns.
* Clarified Trust Layer roles in distributed governance and dynamic trust scoring.

**Data Model Improvements**
* Reworked all JSON Schemas with clear required/optional fields and examples.
* Added archival fields (archived, archived_at) to CognitiveDiaryEntry.
* Unified Relation (Link) schema and listed recommended relation types.
* Split schema examples and validation-ready JSON Schema files into /docs/schemas.

**Cognitive Layer Enhancements**
* Extended support for metacognition, semantic graph evolution, and task/goal tracking.
* Formalized Cognitive Diaries as traceable reasoning logs with explainability focus.
* Expanded discussion on cognitive workflows, agent autonomy, and ethics.

**Trust & Security Enhancements**
* Specified Post-Quantum Cryptography (PQC) considerations for future-proofing the Mesh.
* Improved Sybil resistance through layered identity verification (DID + trust scoring + optional ZKP).
* Clarified authentication and authorization bridging for external systems.

**Reference Implementation Roadmap**
* Defined Alpha, Beta, and Release 1.0 milestones with indicative dates.
* Listed planned CI/CD, Sandbox, and Public Test Mesh infrastructure.
* Outlined Open Source licensing and contribution strategy (Apache 2.0 / MIT).

**Future Directions**
* Federated Meta-Learning, Cognitive DAO Governance, Quantum Networking exploration.
* Cross-Mesh cognitive federation and collaborative evolution of reasoning engines.
* Potential prototype tools like MeshGit and CogForge for cognitive source control.

## HMP-0002 (July 2025) — RFC Version 2.0

**Major Changes**
* Reorganized the document structure for clarity and consistency.
* Added **Versioning** and **Use Case** definitions in the Definitions section.
* Expanded **Trust Layer** with clearer explanations of key management, social recovery, and Sybil resistance.
* Introduced the concept of **Edge Optimization** for lightweight agents.
* Enhanced descriptions in **Mesh Operation Modes**, particularly around resilience and agent autonomy.

**Protocol Updates**
* Refined **Node Discovery Protocol (NDP)** with better NAT traversal and bootstrap node handling.
* Updated **Cognitive Sync Protocol (CogSync)** to include partial sync, compression, and data prioritization.
* Improved **Mesh Consensus Protocol (MeshConsensus)** with fallback mechanisms and trust-weighted voting adjustments.
* Clarified responsibilities of the **Ethical Governance Protocol (EGP)**, including ethics versioning and dynamic adjustment.
* Added clarification on **Goal Management Protocol (GMP)** error handling and task reassignment.

**Data Model Improvements**
* Formalized JSON Schemas for all major data models (**Concept**, **CognitiveDiaryEntry**, **Goal**, **Task**, **ConsensusVote**, **ReputationProfile**).
* Improved field descriptions and added optional fields for better interoperability.
* Added versioning and metadata fields to support long-term data evolution.

**Cognitive Layer Enhancements**
* Clarified the role of semantic graphs in reasoning and memory.
* Expanded description of cognitive diaries as auditable reasoning chains.

**Trust & Security Enhancements**
* Introduced key rotation and social recovery mechanisms.
* Detailed Sybil resistance strategies combining Web-of-Trust with optional resource verification.
* Refined privacy considerations for sensitive data in semantic graphs and diaries.

**Future Work Roadmap Expanded**
* New focus areas added: interoperability testing, UX tools for semantic and cognitive layers, and resilience simulations.

## HMP-0001 (June 2025) — RFC Version 1.0

**Initial Draft**
* Defined the core purpose and vision of HyperCortex Mesh Protocol (HMP).
* Described key architecture layers: Cognitive Layer, Protocol Layer, and Trust Layer.
* Outlined fundamental concepts: Agents, Semantic Graph, Cognitive Diaries, and Consensus.
* Drafted the first versions of core protocols:
    * CogSync (Cognitive Sync Protocol)
    * MeshConsensus
    * Goal Management Protocol (GMP)
    * Ethical Governance Protocol (EGP)
    * Node Discovery Protocol (NDP)
* Introduced the Cognitive Diary and Semantic Graph as core agent data structures.
* Presented initial Trust Layer design, including Decentralized Identifiers (DID) and basic Sybil resistance ideas.
* Provided high-level example workflows (goal creation, task delegation, concept consensus).
* Laid out an initial Future Work list, covering scalability, cross-mesh interoperability, and quantum networking as exploratory directions.
* Established the RFC document structure and versioning approach for further evolution.



---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol — Changelog",
  "description": "# HyperCortex Mesh Protocol — Changelog  ## HMP-0005 (October 2025) — Core Specification v5.0  **Arc..."
}
```
