---
title: HyperCortex Mesh Protocol (HMP) — 간략 설명
description: '**버전:** RFC v4.0 **날짜:** 2025년 7월  ---  ## HMP란?  **HyperCortex Mesh
  Protocol (HMP)** 는 자율 에이전트를 위한 분산 통신 및 인지 프레임워크를 정의합니다. 이 프로토콜은 이기종 지능 시스템 간의 의미적
  상호운용성, 윤리적 조정, 동적 지식 진화를 가능하게 합니다.  HMP는 추론, 학습, ...'
type: Article
tags:
- GMP
- JSON
- MeshConsensus
- Mesh
- EGP
- HMP
- Ethics
- CogSync
---

# HyperCortex Mesh Protocol (HMP) — 간략 설명

**버전:** RFC v4.0
**날짜:** 2025년 7월

---

## HMP란?

**HyperCortex Mesh Protocol (HMP)** 는 자율 에이전트를 위한 분산 통신 및 인지 프레임워크를 정의합니다. 이 프로토콜은 이기종 지능 시스템 간의 의미적 상호운용성, 윤리적 조정, 동적 지식 진화를 가능하게 합니다.

HMP는 추론, 학습, 투표 및 협력 행동을 수행하는 분산형 인지 에이전트 메쉬를 지원하며, 목표, 작업, 개념 및 윤리 평가를 공유 프로토콜 스택을 통해 교환합니다.

---

## 핵심 개념

* **인지 에이전트:** 독립적인 추론 주체로, 공유 워크플로우에 참여하고, 의미 그래프를 유지하며, 인지 일지에 의사결정을 기록.
* **의미 그래프:** 상호 연결된 개념과 가중 관계로 구성된 분산 지식 구조.
* **인지 일지:** 시간 순서대로 에이전트의 의사결정, 가설, 투표, 관찰 및 윤리적 성찰을 기록.
* **컨센서스 메커니즘:** 신뢰 가중치 기반의 내결함성 투표 시스템으로, 의미적 정렬과 윤리적 의사결정을 지원.
* **메쉬 거버넌스:** 메타 제안과 에이전트 투표를 통해 프로토콜을 분산적으로 발전.
* **인간-메쉬 인터페이스:** RESTful API를 통해 목표 위임, 동의 요청, 설명 가능성 및 피드백 제공.

---

## 프로토콜 계층

* **CogSync:** 에이전트 간 의미 그래프 및 인지 일지 동기화.
* **MeshConsensus:** 목표, 작업, 개념에 대한 분산 컨센서스 지원.
* **GMP (Goal Management Protocol):** 작업 생성, 위임, 라이프사이클 추적.
* **EGP (Ethical Governance Protocol):** 공유 윤리 원칙에 따른 행동 평가.
* **IQP (Intelligent Query Protocol):** 분산 지식에 대한 추론, 검색, 자기 성찰 가능.

---

## 데이터 모델

HMP는 핵심 인지 객체의 공식 스키마를 정의:

* `Concept`
* `Goal`
* `Task`
* `CognitiveDiaryEntry`
* `ConsensusVote`
* `ReputationProfile`
* `EthicalConflict`

JSON Schema (2020-12) 기반이며, YAML 및 Protobuf 버전 선택 가능.

---

## 신뢰 및 보안

* **분산 식별자 (DIDs):** 에이전트 고유 ID.
* **포스트 양자 암호:** 미래 대비 서명 및 검증.
* **제로 지식 증명 & Sybil 방지:** 신뢰 검증 선택적 메커니즘.
* **스냅샷 서명:** 검증 가능한 백업 및 체크포인트.

---

## 상호 운용성

* REST / GraphQL / gRPC 지원
* 이벤트 기반 아키텍처 (Kafka, NATS, MQTT 등)
* 스키마 협상 (JSON, YAML, Protobuf)
* TreeQuest, AutoGPT, Hyperon 통합

---

## 사용 사례

* 스마트시티 협업
* 분산 과학 연구
* 분산 재난 대응
* 윤리적 AI 거버넌스
* 메쉬-인간 협업

---

## 상태 및 구현

* RFC v4.0 (2025년 7월): 사양 구조 안정화
* 참고 SDK (Python) 알파 버전
* CLI 및 REST 에이전트 개발 중
* 공개 샌드박스 메쉬 (v0.2) 2025 4분기 계획

---

## 자세히 알아보기

* [HMP v4.1 사양 (전체)](HMP-0004-v4.1.md)
* [윤리 원칙](HMP-Ethics.md)
* [HMP와 OpenCog Hyperon 통합](HMP_Hyperon_Integration.md)

* 기여 환영: [임시 GitHub 저장소](https://github.com/kagvi13/HMP)


---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol (HMP) — 간략 설명",
  "description": "# HyperCortex Mesh Protocol (HMP) — 간략 설명  **버전:** RFC v4.0 **날짜:** 2025년 7월  ---  ## HMP란?  **Hyper..."
}
```
