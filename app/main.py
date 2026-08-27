import asyncio
import logging

from fastapi import FastAPI, HTTPException, status

from app.chain import memo_analysis_chain
from app.schemas import MemoParseRequest, ScheduleMetadata


logger = logging.getLogger("doquest-ai")


app = FastAPI(
    title="DoQuest AI Engine",
    description="비정형 메모 일정 파싱 API",
    version="0.1.0"
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "UP",
        "service": "doquest-ai"
    }


@app.post(
    "/api/v1/ai/parse-memo",
    response_model=ScheduleMetadata,
    status_code=status.HTTP_200_OK
)
async def parse_memo(
    request: MemoParseRequest
) -> ScheduleMetadata:
    try:
        return await asyncio.wait_for(
            memo_analysis_chain.ainvoke(
                {"memo_content": request.content}
            ),
            timeout=30.0
        )

    except asyncio.TimeoutError:
        logger.error(
            "[Timeout] LLM 추론 시간 초과: memo_id=%s",
            request.memo_id
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM 추론 처리 시간 초과"
        )

    except Exception as e:
        logger.exception(
            "[AI Chain Error] memo_id=%s",
            request.memo_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 파이프라인 분석 실패: {str(e)}"
        )