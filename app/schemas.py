from typing import List, Optional

from pydantic import BaseModel, Field


class MemoParseRequest(BaseModel):
    memo_id: Optional[int] = Field(
        default=None,
        description="메모 고유 ID"
    )
    member_id: int = Field(
        description="요청 회원 ID"
    )
    content: str = Field(
        min_length=1,
        description="사용자가 작성한 자유 메모 원본"
    )


class ScheduleMetadata(BaseModel):
    is_schedule: bool = Field(
        description="일정, 약속, 마감일 또는 할 일 포함 여부"
    )
    title: str = Field(
        description="정제된 일정 제목"
    )
    scheduled_at: Optional[str] = Field(
        default=None,
        description="일정 날짜. YYYY-MM-DD 형식이며 날짜가 없으면 null"
    )
    location: Optional[str] = Field(
        default=None,
        description="장소 정보. 없으면 null"
    )
    summary_info: str = Field(
        description="일정 수행에 필요한 핵심 내용 요약"
    )
    action_links: List[str] = Field(
        default_factory=list,
        description="관련 링크 목록. 현재 MVP에서는 빈 배열"
    )