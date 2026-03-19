"""Task request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.common import Quadrant


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("제목을 입력해주세요")
        if len(stripped) > 200:
            raise ValueError("제목은 200자를 초과할 수 없습니다")
        return stripped


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = None
    quadrant: Optional[Quadrant] = None
    completed: Optional[bool] = None
    user_override: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("제목을 입력해주세요")
        if len(stripped) > 200:
            raise ValueError("제목은 200자를 초과할 수 없습니다")
        return stripped


class AIClassification(BaseModel):
    """AI classification result for a task."""

    urgency: Optional[str] = None
    importance: Optional[str] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None
    parsed_datetime: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    user_id: str
    title: str
    quadrant: Optional[Quadrant] = None
    urgency: Optional[str] = None
    importance: Optional[str] = None
    confidence: float = 0.0
    parsed_datetime: Optional[datetime] = None
    completed: bool = False
    user_override: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
