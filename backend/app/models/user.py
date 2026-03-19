"""User data model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User entity for DynamoDB storage."""

    id: str
    email: str
    hashed_password: str
    created_at: datetime = field(default_factory=datetime.utcnow)
