"""Task data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Task entity for DynamoDB storage."""

    id: str
    user_id: str
    title: str
    quadrant: Optional[str] = None
    urgency: Optional[str] = None
    importance: Optional[str] = None
    confidence: float = 0.0
    parsed_datetime: Optional[datetime] = None
    completed: bool = False
    user_override: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
