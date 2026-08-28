# DoQuest AI

DoQuest Spring Boot 서버와 연동되어 사용자의 비정형 메모에서 일정 정보를 추출하는 AI 마이크로서비스입니다.

현재 구현 범위는 `FastAPI + LangChain LCEL + OpenAI Structured Output` 기반의 일정 파싱입니다. Vector DB와 RAG는 향후 고도화 항목이며 아직 현재 파이프라인에는 포함되지 않습니다.

## Revision History

| 개정일자 | 버전 | 주요 변경 및 반영 내용 | 작성자 |
| :--- | :--- | :--- | :--- |
| 2026.08.17 | v0.1.0 | FastAPI 및 LangChain 기반 AI 파이프라인 초기 환경 구축 | Janggeun |
| 2026.08.24 | v0.2.0 | FastAPI-Spring 메모 파싱 E2E 연동 | Janggeun |
| 2026.08.27 | v0.2.1 | Gemini API 장애 대응을 위해 LLM Provider를 OpenAI로 전환 | Janggeun |
| 2026.08.28 | v0.3.0 | OpenAI Structured Output, API 계약 및 pytest 최신화 | Janggeun |

## Current Architecture

```text
[Client]
   |
   | POST /api/v1/memos
   v
[Spring Boot]
   |
   | DB commit
   | @TransactionalEventListener(AFTER_COMMIT)
   | @Async("aiTaskExecutor")
   v
[FastAPI]
   |
   | Pydantic request validation
   | LangChain LCEL prompt pipeline
   | OpenAI Structured Output
   v
[ScheduleMetadata response]
   |
   v
[Spring Boot: Memo parsing status update]
```

Spring은 AI 응답을 받은 뒤 현재 `Memo.isParsed` 상태를 갱신합니다. AI 분석 결과 저장·조회와 사용자 확인 후 Schedule을 생성하는 전체 Two-Phase 흐름은 다음 개발 단계입니다.

## Technology Stack

- Python 3.11+
- FastAPI
- Pydantic v2 / pydantic-settings
- LangChain Core / LangChain OpenAI
- OpenAI API
- pytest / HTTPX

기본 모델은 `OPENAI_MODEL` 환경변수로 설정하며, 값이 없으면 `gpt-5.6-luna`를 사용합니다.

## API

### Health Check

```http
GET /health
```

응답 예시:

```json
{
  "status": "UP",
  "service": "doquest-ai"
}
```

### Parse Memo

```http
POST /api/v1/ai/parse-memo
Content-Type: application/json
```

요청 예시:

```json
{
  "memo_id": 12,
  "member_id": 1,
  "content": "이번 주 금요일 서울 스터디카페에서 스프링 시큐리티 정리하기"
}
```

응답 예시:

```json
{
  "is_schedule": true,
  "title": "스프링 시큐리티 정리",
  "scheduled_at": "2026-08-28",
  "location": "서울 스터디카페",
  "summary_info": "스프링 시큐리티의 인증·인가 구조 정리",
  "action_links": []
}
```

`scheduled_at`은 `YYYY-MM-DD` 형식이며 날짜를 판단할 수 없으면 `null`입니다. RAG가 구현되기 전까지 `action_links`는 빈 배열을 반환합니다.

## Processing Flow

1. Pydantic이 `memo_id`, `member_id`, `content` 요청을 검증합니다.
2. KST 기준 오늘 날짜를 프롬프트에 주입합니다.
3. LangChain LCEL이 메모와 프롬프트를 OpenAI 모델에 전달합니다.
4. `with_structured_output(ScheduleMetadata, method="json_schema")`로 응답 구조를 제한합니다.
5. 호출이 30초를 초과하면 `504 Gateway Timeout`을 반환합니다.
6. 그 밖의 AI 파이프라인 오류는 `500 Internal Server Error`로 처리합니다.

## Local Setup

`.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.6-luna
```

의존성을 설치하고 서버를 실행합니다.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## Tests

```bash
pytest -q
```

현재 테스트는 다음 항목을 검증합니다.

- Health Check 성공
- 메모 파싱 성공 및 최신 `ScheduleMetadata` 계약
- 필수 요청 필드 누락 시 `422 Unprocessable Entity`

## Roadmap

- AI 분석 결과 저장·조회
- 사용자 확인 후 Schedule 생성 Two-Phase 흐름
- 실패 작업 상태 관리 및 재시도
- Chroma 기반 유사 퀘스트 검증
- RAG 기반 공식 문서 검색·요약
- Docker Compose 및 운영 배포
