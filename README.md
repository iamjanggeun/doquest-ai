# Revision History

| 개정일자 | 버전 | 주요 변경 및 반영 내용 | 작성자 |
| :--- | :--- | :--- | :--- |
| 2026.08.17 | v0.1.0 | FastAPI 및 LangChain 기반 AI 파이프라인 초기 환경 구축 (.venv, .gitignore, Git 리포지토리 연동) | Janggeun |
| 2026.08.24 | v0.2.0 | FastAPI <-> Spring E2E 테스트 메모 파싱 성공 | Janggeun |
| 2026.08.27 | v0.2.1 | GeminiAPI 이슈 발생으로 LLM Provider 변경 (Gemini -> OpenAI) | Janggeun |

---

# DoQuest-AI: DoQuest에 연동되는 지능형 일정 파싱 및 퀘스트 추천 마이크로서비스

FastAPI와 LangChain LCEL을 활용하여 비정형 자유 메모를 분석하고, 구조화된 시계열  일정 데이터 및 RAG 기반 추천 정보를 생성하는 AI 마이크로서비스입니다.

---

## 📌 Project Architecture Overview

```text
[Client / User]
       │
       ▼ (자유 메모 작성)
[Spring Boot Server (DoQuest-server)]
       │
       ▼ HTTP REST (비동기 분석 위임)
[FastAPI AI Server (doquest-ai)]
       │
       ├─▶ [Pydantic v2] : Request Payload 검증
       ├─▶ [LangChain LCEL Pipeline] : 시계열/컨텍스트 분석 + Prompt Template
       ├─▶ [OpenAI LLM Engine] : gpt-4o-mini 구조화 추론
       └─▶ [JsonOutputParser] : Type-safe JSON Output 생성
       │
       ▼ Response (is_schedule, target_date, summary_info, action_links)
[Spring Boot Server] ──▶ 캘린더 등록 및 D-3 퀘스트 전환 서빙
