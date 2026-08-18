from pydantic import BaseModel, Field
from typing import List, Optional

class MemoParseRequest(BaseModel):
    member_id: int = Field(description="요청 회원 ID", default=1)
    content: str = Field(description="사용자가 작성한 자유 메모 원본", min_length=1)

class ScheduleMetadata(BaseModel):
    is_schedule: bool = Field(description="일정(시간/날짜/할일) 포함 여부")
    title: str = Field(description="정제된 일정 제목 (명사형 요약)")
    target_date: Optional[str] = Field(description="추출된 날짜 (YYYY-MM-DD 포맷, 없으면 null)", default=None)
    summary_info: str = Field(description="일정 수행에 필요한 핵심 정보 요약")
    action_links: List[str] = Field(description="관련 추천 웹 링크 리스트", default=[])