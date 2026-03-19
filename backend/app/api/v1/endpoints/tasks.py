from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from ....api.deps import get_current_user
from ....models.user import User
from ....repositories.task_repository import TaskRepository
from ....schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ....services.ai_service import AIService
from ....services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service() -> TaskService:
    return TaskService(TaskRepository(), AIService())


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = task_service.create_task(current_user.id, payload.title)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
def get_user_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> list[TaskResponse]:
    tasks = task_service.get_user_tasks(current_user.id)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = task_service.get_task(current_user.id, task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    task = task_service.update_task(current_user.id, task_id, payload)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Response:
    task_service.delete_task(current_user.id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
