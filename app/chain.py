from datetime import date
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import settings
from app.schemas import ScheduleMetadata

# Gemini 모델 인스턴스화
llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key,
    temperature=0
)

# JSON 파서 및 프롬프트 템플릿
# 추후 이번주나 다음주와 같은 표현도 추가.
parser = JsonOutputParser(pydantic_object=ScheduleMetadata)

prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 사용자의 메모를 분석하여 캘린더 일정 데이터를 구조화하는 AI 어시스턴트입니다.
오늘 기준 날짜는 {today}입니다.
메모 내용에서 일정/시간 표현을 찾아 YYYY-MM-DD 포맷으로 변환하고, 관련 가이드 요약 및 링크를 생성하세요.

반드시 아래 JSON 스키마 규격으로만 응답해야 합니다:
{format_instructions}"""),
    ("human", "{memo_content}")
])

# LCEL 체인 조합
memo_analysis_chain = (
    {
        "memo_content": lambda x: x["memo_content"],
        "today": lambda _: str(date.today()),
        "format_instructions": lambda _: parser.get_format_instructions()
    }
    | prompt
    | llm
    | parser
)