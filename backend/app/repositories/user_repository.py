from datetime import datetime
from typing import Any

from boto3.dynamodb.conditions import Attr

from ..core.database import get_dynamodb_table
from ..models.user import User


class UserRepository:
    def __init__(self, table: Any = None):
        self.table = table or get_dynamodb_table()

    def create_user(self, user: User) -> User:
        self.table.put_item(Item=self._to_item(user))
        return user

    def get_user_by_email(self, email: str) -> User | None:
        response = self.table.get_item(Key={"PK": f"USER#{email}", "SK": "PROFILE"})
        item = response.get("Item")
        if item is None:
            return None
        return self._to_entity(item)

    def get_user_by_id(self, user_id: str) -> User | None:
        response = self.table.scan(
            FilterExpression=Attr("SK").eq("PROFILE") & Attr("id").eq(user_id)
        )
        items = response.get("Items", [])
        if not items:
            return None
        return self._to_entity(items[0])

    def _to_item(self, user: User) -> dict[str, str]:
        return {
            "PK": f"USER#{user.email}",
            "SK": "PROFILE",
            "id": user.id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at.isoformat(),
        }

    def _to_entity(self, item: dict[str, str]) -> User:
        return User(
            id=item["id"],
            email=item["email"],
            hashed_password=item["hashed_password"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
