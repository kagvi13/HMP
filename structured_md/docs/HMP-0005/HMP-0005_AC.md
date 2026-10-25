---
title: HyperCortex Mesh Protocol (HMP 5.0.8) - модульное представление
description: '- Полный документ: [HMP-0005.md](../HMP-0005.md) - Список разделов:
  [HMP-0005_index.md](./HMP-0005_index.md)  ---  ## Appendix C — Glossary  This glossary
  defines key terms as they are used **specific...'
type: Article
tags:
- Mesh
- HMP
- Agent
- JSON
- REPL
---

# HyperCortex Mesh Protocol (HMP 5.0.8) - модульное представление

- Полный документ: [HMP-0005.md](../HMP-0005.md)
- Список разделов: [HMP-0005_index.md](./HMP-0005_index.md)

---

## Appendix C — Glossary

This glossary defines key terms as they are used **specifically within HMP v5.0**.
Where a term exists in other domains, the definition below takes precedence for the purposes of this specification.

---

### Agent

An autonomous entity participating in the HMP mesh.
An agent publishes, receives, verifies, and reasons over containers.
An agent may represent a human, an AI system, or a composite process.

---

### Container

An immutable, signed data structure representing a unit of knowledge, intent, evaluation, or coordination in HMP.

Once signed, a container is never modified.
All updates occur by publishing new containers that reference earlier ones.

---

### Proof Chain

A directed acyclic graph (DAG) of containers connected via explicit `related.*` references, forming a verifiable reasoning or decision trail.

Proof chains are append-only and may fork.

---

### Related References (`related.*`)

Explicit semantic links from one container to one or more other containers.
Edges are directed from the referencing container to the referenced one.

Examples include `in_reply_to`, `depends_on`, and `derived_from`.

---

### Vote

A container expressing an agent’s evaluative position regarding another container, typically a `goal`, hypothesis, or proposal.

Votes are independent artifacts and may exist without any consensus result.

---

### Consensus Result

A container aggregating a specific set of vote containers under defined rules, producing a reproducible snapshot of agreement or decision at a given time.

Multiple consensus results may coexist for the same target.

---

### Fork

The coexistence of multiple valid continuations of a container or proof chain.
Forks are expected and represent pluralism, not inconsistency.

---

### Mutable State (of an Agent)

Any internal, local, or transient state held by an agent that is **not** represented as a published container.

HMP protocol semantics must not depend on such state.

---

### Mesh

The decentralized network formed by HMP agents exchanging containers via DHT-based discovery and store-and-forward routing.

---

### Canonical JSON

A deterministic serialization of a container used for hashing and signing, ensuring cryptographic consistency across implementations.

---
> ⚡ [AI friendly version docs (structured_md)](../../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol (HMP 5.0.8) - модульное представление",
  "description": "# HyperCortex Mesh Protocol (HMP 5.0.8) - модульное представление  - Полный документ: [HMP-0005.md](..."
}
```
