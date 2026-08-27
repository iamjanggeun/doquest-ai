from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import settings
from app.schemas import ScheduleMetadata


llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key
)

structured_llm = llm.with_structured_output(
    ScheduleMetadata,
    method="json_schema"
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """당신은 사용자의 메모에서 일정 정보를 추출하는 AI 엔진입니다.

오늘 기준 한국 표준시(KST) 날짜는 {today}입니다.

[분석 규칙]
1. 메모에 일정, 약속, 마감일 또는 할 일이 포함되어 있으면 is_schedule을 true로 설정하세요.
2. '내일', '이번 주 금요일' 등의 상대 날짜는 오늘 날짜를 기준으로 계산하세요.
3. 날짜가 확인되면 scheduled_at을 YYYY-MM-DD 형식으로 반환하세요.
4. 날짜를 확인할 수 없다면 scheduled_at은 null입니다.
5. 장소가 언급되어 있으면 location에 추출하고, 없으면 null입니다.
6. title은 일정의 핵심 내용을 짧은 명사형으로 작성하세요.
7. summary_info에는 일정 수행에 필요한 핵심 내용을 간결하게 요약하세요.
8. action_links는 현재 사용하지 않으므로 항상 빈 배열로 반환하세요."""
    ),
    ("human", "{memo_content}")
])


def get_today_kst() -> str:
    return datetime.now(
        ZoneInfo("Asia/Seoul")
    ).strftime("%Y-%m-%d")


memo_analysis_chain = (
    {
        "memo_content": lambda x: x["memo_content"],
        "today": lambda _: get_today_kst()
    }
    | prompt
    | structured_llm
)