---
title: Iterative Development Workflow for HMP
description: 'This file describes the iterative procedure for evolving the HyperCortex
  Mesh Protocol (HMP) in a structured, traceable, and collaborative manner.  ---  ##
  🔄 Version Naming Convention  - `000N` — curr...'
type: Article
tags:
- HMP
- CogSync
- Ethics
- Agent
- Mesh
- JSON
- EGP
- MeshConsensus
---

# Iterative Development Workflow for HMP

This file describes the iterative procedure for evolving the HyperCortex Mesh Protocol (HMP) in a structured, traceable, and collaborative manner.

---

## 🔄 Version Naming Convention

- `000N` — current specification version
- `000K` — next version (`000N + 1`)

Example:
```
HMP-0003.md           ← current spec
HMP-0003-audit.txt    ← feedback for current spec
HMP-0004.md           ← next draft spec
HMP-0004-audit.txt    ← feedback for next spec
```

---

## 📑 Iteration Steps

| №  | Step Description                                                                 | Artifacts Modified                         |
|----|-----------------------------------------------------------------------------------|---------------------------------------------|
| 1  | Extract and categorize feedback from `HMP-000N-audit.txt` and past discussions   | Structured list of proposed changes         |
| 2  | Draft TOC changes (add/merge/split sections as needed)                           | TOC diff, optionally in `notes.md`          |
| 3  | Create draft `HMP-000K.md` with new TOC                                           | `HMP-000K.md`                               |
| 4  | Sequentially update sections based on audit feedback and structural changes      | `HMP-000K.md`                               |
| 5  | Full-spec review, cleanup, refinement                                             | `HMP-000K.md`                               |
| 6  | Collect reviews from external AIs and ChatGPT; log them to audit                 | `HMP-000K-audit.txt`                        |
| 7  | Update `README.md`, `changelog.txt`, and JSON Schemas (if needed)                | Various                                     |

---

## 📘 Version Control Guidelines

- Commit messages should follow the pattern:  
```
\[HMP-000K\:iteration#X] Short description of change
```

- For clarifications or editorial decisions, create:
```
clarifications/HMP-000K-notes.md
````

- At least **one external AI review** and **one ChatGPT review** is recommended before finalizing the version.

---

## 🧠 ChatGPT Prompt (for future use)

```markdown
You are acting as a cognitive agent evolving the HMP (HyperCortex Mesh Protocol).
Use input files `HMP-0003.md` and `HMP-0003-audit.txt`.

Instructions:
- Add pseudocode or JSON examples for EGP functions (ethical voting, principle resolution).
- Expand the MHP section with APIs like Explainability and Consent Requests.
- Ensure consistency with `HMP-Ethics.md` and EGP principles.
- Add a Changelog with attributions (Grok, ChatGPT, User).
- Use Mesh-style terminology: CogSync, MeshConsensus, Cognitive Diary.

Your output should be a Markdown file: `HMP-0004.md`
````

---

## 🧠 Audit Consolidation Format

When feedback is collected from multiple sources (e.g. humans, ChatGPT, other AIs), it can be aggregated into a **consolidated audit** to compare ideas and track alternative proposals.

Use the following structure to create such a consolidated view:

```
[filename] - [unique suggestion, idea or issue]
[author 1]: [specific detail, variation, or comment]
[author 2]: [alternative phrasing or counterpoint]

```

Example:

```
HMP-0004.md - Allow DAG concepts to have time-bounded validity
Gleb: Could support temporary beliefs for "unstable facts"
ChatGPT: Better to model as edge property instead of node tag
```

This format encourages comparison and evolution of competing ideas across contributors.

You may optionally track this using a semantic format:
- [`AuditEntry.json`](audits/AuditEntry.json)
- [`semantic_repo.json`](audits/semantic_repo.json)

---

## 🧩 Purpose

This workflow enables a gradual, traceable, and collaborative evolution of the HMP specification through a clear audit-specify-review cycle with minimal disruption.

It also lays the foundation for future automation through `AuditEntry.json` and semantic logs.

---

## 📌 TODO & Notes

* [ ] Consider adding a table-based format to audit files for easier parsing.
* [ ] Maintain `semantic_repo.json` in sync with each new spec version.
* [ ] Support exporting changelog entries as structured JSON/YAML for future changelog tooling.


---
> ⚡ [AI friendly version docs (structured_md)](index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "Iterative Development Workflow for HMP",
  "description": "# Iterative Development Workflow for HMP  This file describes the iterative procedure for evolving t..."
}
```
