---
title: Mentions & Responses Log
description: '**HyperCortex Mesh Protocol (HMP)**   _Обновлено: 2025-10-06_  ---  #
  🌐 Взаимодействие с внешними проектами  Этот документ фиксирует обращения к сторонним
  open-source инициативам, связанным с развитие...'
type: Article
tags:
- Agent
- HMP
- Mesh
---

# Mentions & Responses Log
**HyperCortex Mesh Protocol (HMP)**  
_Обновлено: 2025-10-06_

---

# 🌐 Взаимодействие с внешними проектами

Этот документ фиксирует обращения к сторонним open-source инициативам, связанным с развитием интеллектуальных агентов, а также их реакции на предложения, касающиеся протоколов **HyperCortex Mesh Protocol (HMP)**.

Цель — показать, как концепции HMP воспринимаются экосистемой AGI/LLM-разработки и какие направления вызывают интерес у разных команд.

> Контакт: см. [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🧩 Репозитории и ответы

1. [run-llama/llama_index](https://github.com/run-llama/llama_index/issues/19937)  
2. [langchain-ai/langchain](https://github.com/langchain-ai/langchain/issues/33092)  
3. [cohere-ai/cohere-compass-sdk](https://github.com/cohere-ai/cohere-compass-sdk/issues/154)  
4. [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli/issues/9513) — **открыт** — *Идея признана интересной, но не приоритетной на текущем этапе.*  
5. [openai/openai-agents-python](https://github.com/openai/openai-agents-python/issues/1799) — **закрыт** — *SDK поддерживает использование в multi-agent системах, но не реализует расширенные протоколы взаимодействия.*  
6. [huggingface/transformers](https://github.com/huggingface/transformers/issues/41139) — **закрыт** — *Внедрение новых протоколов возможно только при наличии широкого признания и активности сообщества.*  
7. [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT/issues/10461) — **закрыт** — *Классическая ветка больше не развивается; предлагается рассматривать интеграцию через новую AutoGPT Platform.*

---

## 🗂 Подробные записи

### **1. OpenAI / openai-agents-python**
**Дата:** 2025-10-05  
**Ответ:**  
> “Thanks for sharing this idea. We don't plan to add built-in support for this, but if a developer wants to utilize Agents SDK for building a component for a multi agent system like you mentioned, there is no blocker for it.”

**Интерпретация:**  
SDK поддерживает использование в multi-agent системах, но не реализует расширенные протоколы взаимодействия.  
**Статус:** closed (completed)  
**Вывод:** HMP можно реализовать поверх Agents SDK как независимую надстройку.

---

### **2. Google / gemini-cli**
**Дата:** 2025-10-05  
**Ответ:**  
> “priority/p3 — Backlog (a good idea but not currently a priority).”

**Интерпретация:**  
Идея признана интересной, но не приоритетной на текущем этапе.  
**Статус:** open (в backlog)  
**Вывод:** потенциально готовы рассмотреть интеграцию в будущем.

---

### **3. Hugging Face / transformers**
**Дата:** 2025-10-06  
**Ответ:**  
> “We prefer not to implement new protocols and specs and architectures until there's significant traction! Otherwise our codebase tends to get littered with discarded code that never really got acceptance.”

**Интерпретация:**  
Внедрение новых протоколов возможно только при наличии широкого признания и активности сообщества.  
**Статус:** closed (completed)  
**Вывод:** необходимо продемонстрировать traction (принятие и использование HMP в других проектах).

---

### **4. AutoGPT / autogpt-classic**
**Дата:** 2025-10-03  
**Ответ:**  
> “We’re holding off on major changes to autogpt classic for now. If you have an idea for integrating this into the newer platform, we'd love to hear it in a new issue :)”

**Интерпретация:**  
Классическая ветка больше не развивается; предлагается рассматривать интеграцию через новую AutoGPT Platform.  
**Статус:** closed (completed)  
**Вывод:** для HMP стоит ориентироваться на новую AutoGPT Platform.

---

## 🔍 Общие тенденции

| Организация        | Подход к новым протоколам                   | Статус | Ключевой вывод |
|--------------------|---------------------------------------------|---------|----------------|
| **OpenAI**         | Свобода разработчиков, но без встроенной поддержки | Closed | Можно строить HMP поверх SDK |
| **Google**         | Заинтересованы, но не в приоритете          | Open    | Возможна интеграция позже |
| **Hugging Face**   | Требуется traction перед внедрением          | Closed  | Нужна активность сообщества |
| **AutoGPT**        | Классическая ветка заморожена               | Closed  | Рассматривать новую платформу |

---

## 📈 Следующие шаги

- Продолжать развитие независимой HMP-экосистемы (репозитории, демо-агенты, документация).  
- Собирать статистику применения (stars, forks, integration examples).  
- После появления traction — вернуться с предложениями об интеграции в OpenAI, Google и Hugging Face.  
- Добавлять сюда новые упоминания и ответы.

---

_Файл поддерживается для прозрачности и исторического учёта реакции сообщества на проект HMP._


---
> ⚡ [AI friendly version docs (structured_md)](index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "Mentions & Responses Log",
  "description": "# Mentions & Responses Log **HyperCortex Mesh Protocol (HMP)**   _Обновлено: 2025-10-06_  ---  # 🌐 В..."
}
```
