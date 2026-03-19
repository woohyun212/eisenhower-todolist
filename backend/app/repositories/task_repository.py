from datetime import datetime
from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key

from ..core.database import get_dynamodb_table
from ..models.task import Task


class TaskRepository:
    GSI1_NAME = "GSI1"

    def __init__(self, table=None):
        self.table = table or get_dynamodb_table()

    def create_task(self, task: Task) -> Task:
        self.table.put_item(Item=self._to_item(task))
        return task

    def get_task(self, user_id: str, task_id: str) -> Task | None:
        response = self.table.get_item(Key={"PK": self._pk(user_id), "SK": self._sk(task_id)})
        item = response.get("Item")
        if item is None:
            return None
        return self._to_entity(item)

    def get_user_tasks(self, user_id: str, quadrant: str | None = None) -> list[Task]:
        pk = self._pk(user_id)
        if quadrant is None:
            items = self._query_all(KeyConditionExpression=Key("PK").eq(pk))
        else:
            items = self._query_all(
                IndexName=self.GSI1_NAME,
                KeyConditionExpression=Key("GSI1PK").eq(pk)
                & Key("GSI1SK").begins_with(self._gsi1sk_prefix(quadrant)),
            )
        return [self._to_entity(item) for item in items]

    def update_task(self, task: Task) -> Task:
        self.table.put_item(Item=self._to_item(task))
        return task

    def delete_task(self, user_id: str, task_id: str) -> None:
        self.table.delete_item(Key={"PK": self._pk(user_id), "SK": self._sk(task_id)})

    def _query_all(self, **query_kwargs: Any) -> list[dict[str, Any]]:
        response = self.table.query(**query_kwargs)
        items = list(response.get("Items", []))
        while "LastEvaluatedKey" in response:
            response = self.table.query(
                **query_kwargs,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
        return items

    def _to_item(self, task: Task) -> dict[str, Any]:
        created_at_str = task.created_at.isoformat()
        item: dict[str, Any] = {
            "PK": self._pk(task.user_id),
            "SK": self._sk(task.id),
            "GSI1PK": self._pk(task.user_id),
            "GSI1SK": self._gsi1sk(task.quadrant, created_at_str),
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "confidence": Decimal(str(task.confidence)),
            "completed": task.completed,
            "created_at": created_at_str,
            "updated_at": task.updated_at.isoformat(),
        }

        if task.quadrant is not None:
            item["quadrant"] = task.quadrant
        if task.urgency is not None:
            item["urgency"] = task.urgency
        if task.importance is not None:
            item["importance"] = task.importance
        if task.parsed_datetime is not None:
            item["parsed_datetime"] = task.parsed_datetime.isoformat()
        if task.user_override is not None:
            item["user_override"] = task.user_override

        return item

    def _to_entity(self, item: dict[str, Any]) -> Task:
        parsed_datetime = self._parse_optional_datetime(item.get("parsed_datetime"))
        return Task(
            id=str(item["id"]),
            user_id=str(item["user_id"]),
            title=str(item["title"]),
            quadrant=item.get("quadrant"),
            urgency=item.get("urgency"),
            importance=item.get("importance"),
            confidence=float(item.get("confidence", 0.0)),
            parsed_datetime=parsed_datetime,
            completed=bool(item.get("completed", False)),
            user_override=item.get("user_override"),
            created_at=self._parse_datetime(item["created_at"]),
            updated_at=self._parse_datetime(item["updated_at"]),
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    @classmethod
    def _parse_optional_datetime(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        return cls._parse_datetime(value)

    @staticmethod
    def _pk(user_id: str) -> str:
        return f"USER#{user_id}"

    @staticmethod
    def _sk(task_id: str) -> str:
        return f"TASK#{task_id}"

    @classmethod
    def _gsi1sk_prefix(cls, quadrant: str) -> str:
        return f"QUADRANT#{quadrant}#DATE#"

    @classmethod
    def _gsi1sk(cls, quadrant: str | None, created_at: str) -> str:
        quadrant_value = quadrant or "NONE"
        return f"{cls._gsi1sk_prefix(quadrant_value)}{created_at}"
