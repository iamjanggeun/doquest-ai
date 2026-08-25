from datetime import datetime
from zoneinfo import ZoneInfo
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import settings
from app.schemas import ScheduleMetadata

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key,
    temperature=0
)

parser = JsonOutputParser(pydantic_object=ScheduleMetadata)

prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 사용자의 메모를 분석하여 일정 데이터를 추출하는 AI 엔진입니다.
오늘 기준 한국 표준시(KST) 날짜는 {today}입니다.

[분석 규칙]
1. 메모에 일정/약속/마감일/할일이 포함되어 있다면 is_schedule을 true로 설정하세요.
2. '내일', '이번 주 금요일' 등의 상대 날짜는 {today}를 기준으로 계산하여 반드시 YYYY-MM-DD 포맷(scheduled_at)으로 변환하세요. 날짜가 없으면 null로 설정하세요.
3. 장소나 위치가 언급되어 있다면 location에 추출하고, 없으면 null로 설정하세요.
4. action_links는 가짜 URL을 생성하지 말고 빈 배열([])로 반환하세요.

반드시 아래 JSON 스키마 규격으로만 응답해야 합니다:
{format_instructions}"""),
    ("human", "{memo_content}")
])

# LCEL 체인 조합
# KST 기준 오늘 날짜 추출 추가
def get_today_kst() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

memo_analysis_chain = (
    {
        "memo_content": lambda x: x["memo_content"],
        "today": lambda _: get_today_kst(),
        "format_instructions": lambda _: parser.get_format_instructions()
    }
    | prompt
    | llm
    | parser
)