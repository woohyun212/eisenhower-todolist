from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from ..models.task import Task
from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskUpdate
from .ai_service import AIService


class TaskService:
    def __init__(self, task_repo: TaskRepository, ai_service: AIService):
        self.task_repo: TaskRepository = task_repo
        self.ai_service: AIService = ai_service

    def create_task(self, user_id: str, title: str) -> Task:
        classification = self.ai_service.classify_task(title)
        now = datetime.now(timezone.utc)
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            quadrant=getattr(classification, "quadrant", None),
            urgency=classification.urgency,
            importance=classification.importance,
            confidence=classification.confidence,
            parsed_datetime=classification.parsed_datetime,
            completed=False,
            created_at=now,
            updated_at=now,
        )
        return self.task_repo.create_task(task)

    def get_user_tasks(self, user_id: str) -> list[Task]:
        return self.task_repo.get_user_tasks(user_id)

    def get_task(self, user_id: str, task_id: str) -> Task:
        task = self.task_repo.get_task(user_id, task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    def update_task(self, user_id: str, task_id: str, data: TaskUpdate) -> Task:
        task = self.get_task(user_id, task_id)
        updates = data.model_dump(exclude_unset=True)

        if "title" in updates:
            task.title = updates["title"]
            # Reclassify task when title is updated
            classification = self.ai_service.classify_task(task.title)
            task.quadrant = getattr(classification, "quadrant", None)
            task.urgency = classification.urgency
            task.importance = classification.importance
            task.confidence = classification.confidence
            task.parsed_datetime = classification.parsed_datetime
        if "quadrant" in updates:
            task.quadrant = updates["quadrant"]
        if "completed" in updates:
            task.completed = updates["completed"]
        if "user_override" in updates:
            task.user_override = updates["user_override"]

        task.updated_at = datetime.now(timezone.utc)
        return self.task_repo.update_task(task)

    def delete_task(self, user_id: str, task_id: str) -> None:
        _ = self.get_task(user_id, task_id)
        self.task_repo.delete_task(user_id, task_id)
