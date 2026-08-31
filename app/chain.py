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

현재 한국 표준시(KST)는 {current_datetime}입니다.

[분석 규칙]
1. 메모에 일정, 약속, 마감일 또는 할 일이 포함되어 있으면 is_schedule을 true로 설정하세요.
2. '내일', '이번 주 금요일', '2시간 뒤' 등의 상대 날짜와 시간은 현재 KST를 기준으로 계산하세요.
3. 날짜가 확인되면 scheduled_at을 YYYY-MM-DD 형식으로 반환하세요.
4. 날짜를 확인할 수 없다면 scheduled_at은 null입니다.
5. 시간이 확인되면 scheduled_time을 24시간제 HH:mm 형식으로 반환하세요.
6. 시간이 언급되지 않았다면 scheduled_time은 null입니다. 마감일처럼 시간이 없는 일정에 임의 시간을 만들지 마세요.
7. 장소가 언급되어 있으면 location에 추출하고, 없으면 null입니다.
8. title은 일정의 핵심 내용을 짧은 명사형으로 작성하세요.
9. summary_info에는 일정 수행에 필요한 핵심 내용을 간결하게 요약하세요.
10. action_links는 현재 사용하지 않으므로 항상 빈 배열로 반환하세요."""
    ),
    ("human", "{memo_content}")
])


def get_current_datetime_kst() -> str:
    return datetime.now(
        ZoneInfo("Asia/Seoul")
    ).strftime("%Y-%m-%d %H:%M:%S %Z")


memo_analysis_chain = (
    {
        "memo_content": lambda x: x["memo_content"],
        "current_datetime": lambda _: get_current_datetime_kst()
    }
    | prompt
    | structured_llm
)
