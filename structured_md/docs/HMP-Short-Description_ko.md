---
title: HyperCortex Mesh Protocol (HMP) — 개요
description: '**버전:** v5.0 (Core Specification Stable)   **날짜:** 2026    ---  ## HMP란
  무엇인가?  **HyperCortex Mesh Protocol(HMP)** 은 자율 에이전트 기반의 분산 인지 네트워크를 구축하기 위한 개방형
  명세입니다.  HMP는 에이전트가 다음을 수행할 수 있도록 합니다:  - 장기적인 인지...'
type: Article
tags:
- HMP
- Mesh
- REPL
- Agent
---

# HyperCortex Mesh Protocol (HMP) — 개요

**버전:** v5.0 (Core Specification Stable)  
**날짜:** 2026  

---

## HMP란 무엇인가?

**HyperCortex Mesh Protocol(HMP)** 은 자율 에이전트 기반의 분산 인지 네트워크를 구축하기 위한 개방형 명세입니다.

HMP는 에이전트가 다음을 수행할 수 있도록 합니다:

- 장기적인 인지 연속성 유지
- 구조화된 지식 교환
- 목표 및 행동의 조정
- 분산 합의 달성
- 이기종 시스템 간 윤리적 정렬

기존의 상태 비저장(stateless) AI API와 달리, HMP는 에이전트를 공유된 추론 및 기억 Mesh에 내재된 지속적 인지 주체로 간주합니다.

---

## 개념적 기반

HMP는 현대 AI 및 AGI 연구의 주요 과제를 다룹니다:

- 장기 기억 연속성의 부족
- 탈중앙화된 조정 메커니즘의 부재
- 자율 에이전트 간 상호운용성의 제한
- 프로토콜 수준의 윤리 거버넌스 부재

HMP는 추론, 기억, 거버넌스, 전송을 명확히 분리하면서도 상호운용 가능하도록 하는 계층형 아키텍처를 제안합니다.

---

## 핵심 개념

### 인지 에이전트

다음과 같은 능력을 갖춘 자율적 개체:

- 내장 또는 외부 AI 모델을 활용한 추론
- 의미 그래프(semantic graph) 유지
- 인지 다이어리에 의사결정 기록
- 분산 조정에 참여

HMP는 두 가지 유형의 에이전트를 정의합니다:

- **Cognitive Core** — 내장 추론 모델과 지속적인 REPL 기반 사고 주기를 갖는 에이전트
- **Cognitive Connector** — 외부 LLM 시스템을 위한 호환 계층 역할을 하는 에이전트

---

### 컨테이너(Containers)

HMP는 **컨테이너**를 원자적 인지 단위로 도입합니다.

컨테이너는 다음 특성을 가집니다:

- 서명됨
- 검증 가능
- Mesh를 통해 전송 가능
- 구현 언어와 구조적으로 독립적

이는 로컬 추론과 분산 조정을 연결하는 역할을 합니다.

---

### 의미 그래프 및 인지 다이어리

- **의미 그래프**는 가중 관계를 포함한 구조화된 지식을 표현합니다.
- **인지 다이어리**는 추론 과정, 가설, 관찰, 성찰을 시간순으로 기록합니다.

이를 통해 사고의 추적 가능성과 기억의 지속성이 보장됩니다.

---

### 분산 조정

HMP는 프로토콜 수준에서 다음 메커니즘을 제공합니다:

- 목표 수명주기 관리
- 분산 합의
- 윤리적 평가
- 에이전트 간 질의 및 자기 성찰(introspection)

거버넌스는 진화적이며 제안 기반 구조를 따릅니다.

---

## 프로토콜 아키텍처 (v5)

HMP는 다음을 분리합니다:

1. **인지 계층** — 추론, 다이어리, 그래프, 평판
2. **컨테이너 계층** — 원자적이고 서명된 상태 표현
3. **코어 프로토콜** — 합의, 거버넌스, 목표 관리, 윤리
4. **전송 계층** — DHT, P2P, libp2p, ANP 또는 사용자 정의 네트워크

이러한 분리는 모듈성, 확장성, 상호운용성을 지원합니다.

---

## 신뢰 및 검증 가능성

- 컨테이너 및 스냅샷의 암호학적 서명
- 평판 프로파일
- 선택적 Sybil 공격 저항 메커니즘
- 포스트 양자 암호와의 미래 지향적 호환성

신뢰는 프로토콜의 핵심 요소로 간주됩니다.

---

## 상호운용성

HMP는 내부 인지 아키텍처를 강제하지 않습니다.

다음과 상호운용이 가능합니다:

- ANP (Agent Network Protocol)
- OpenCog Hyperon
- 이벤트 기반 인프라
- Cognitive Connector를 통한 LLM 기반 시스템

HMP는 단순한 전송 표준화를 넘어 인지적 연속성에 초점을 둡니다.

---

## 활용 예시

- 분산 과학 협업
- 멀티 에이전트 연구 시스템
- AI 윤리 거버넌스 네트워크
- 지속형 AI 동반자
- Mesh 기반 지식 생태계

---

## 현재 상태

- **v5.0 Core Specification — Stable**
- Early exploratory Python drafts (비프로덕션, 참고용)
- 지속적인 아키텍처 개선 진행 중
- 감사(audit) 및 기여 환영

---

## 추가 정보

- [Project Philosophy](PHILOSOPHY.md)
- [HMP-0005 Core Specification](HMP-0005.md)
- [Overview of v5 Architecture (RU)](HMPv5_Overview_Ru.md)

기여 및 토론은 메인 저장소에서 환영합니다.


---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol (HMP) — 개요",
  "description": "# HyperCortex Mesh Protocol (HMP) — 개요  **버전:** v5.0 (Core Specification Stable)   **날짜:** 2026    -..."
}
```
