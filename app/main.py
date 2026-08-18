from fastapi import FastAPI, HTTPException, status
from app.schemas import MemoParseRequest, ScheduleMetadata
from app.chain import memo_analysis_chain

app = FastAPI(
    title="DoQuest AI Engine",
    description="비정형 메모 시계열 파싱 및 RAG 지능형 일정 추천 API",
    version="0.1.0"
)

# 비동기 LCEL 체인 호출 래퍼 함수 (Mocking 타겟)
async def invoke_memo_chain(content: str) -> dict:
    return await memo_analysis_chain.ainvoke({"memo_content": content})

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "UP", "service": "doquest-ai"}

@app.post("/api/v1/ai/parse-memo", response_model=ScheduleMetadata, status_code=status.HTTP_200_OK)
async def parse_memo(request: MemoParseRequest):
    try:
        result = await invoke_memo_chain(request.content)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 파이프라인 분석 실패: {str(e)}"
        )