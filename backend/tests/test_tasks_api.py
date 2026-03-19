from datetime import datetime, timezone
from importlib import import_module

deps_module = import_module("app.api.deps")
tasks_endpoint_module = import_module("app.api.v1.endpoints.tasks")
main_module = import_module("app.main")
user_module = import_module("app.models.user")
task_repository_module = import_module("app.repositories.task_repository")
ai_service_module = import_module("app.services.ai_service")
task_service_module = import_module("app.services.task_service")

get_auth_service = deps_module.get_auth_service
get_task_service = tasks_endpoint_module.get_task_service
app = main_module.app
User = user_module.User
TaskRepository = task_repository_module.TaskRepository
AIService = ai_service_module.AIService
TaskService = task_service_module.TaskService


class _FakeAuthService:
    def __init__(self, user: User):
        self._user = user

    def get_current_user(self, _token: str) -> User:
        return self._user


def _build_user(user_id: str = "test-user-123") -> User:
    return User(
        id=user_id,
        email="test@example.com",
        hashed_password="not-used",
        created_at=datetime.now(timezone.utc),
    )


def _override_dependencies(dynamodb_table, mock_ai_client, user_id: str = "test-user-123"):
    app.dependency_overrides[get_auth_service] = lambda: _FakeAuthService(_build_user(user_id))
    app.dependency_overrides[get_task_service] = lambda: TaskService(
        task_repo=TaskRepository(table=dynamodb_table),
        ai_service=AIService(client=mock_ai_client),
    )


def _clear_overrides():
    _ = app.dependency_overrides.pop(get_auth_service, None)
    _ = app.dependency_overrides.pop(get_task_service, None)


def test_create_task_with_ai(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        response = client.post(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "내일까지 보고서 제출"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "내일까지 보고서 제출"
        assert data["quadrant"] == "DO"
        assert data["confidence"] == 0.85
        assert data["completed"] is False
    finally:
        _clear_overrides()


def test_create_task_ai_failure(client, auth_token, dynamodb_table, mock_ai_client):
    mock_ai_client.chat.completions.create.side_effect = TimeoutError("timeout")
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        response = client.post(
            "/api/v1/tasks",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "오늘 자정까지 과제 제출"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["quadrant"] is None
        assert data["confidence"] == 0
    finally:
        _clear_overrides()


def test_get_user_tasks(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        client.post("/api/v1/tasks", headers=headers, json={"title": "작업 A"})
        client.post("/api/v1/tasks", headers=headers, json={"title": "작업 B"})

        response = client.get("/api/v1/tasks", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert {item["title"] for item in data} == {"작업 A", "작업 B"}
    finally:
        _clear_overrides()


def test_get_task_not_found(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        response = client.get(
            "/api/v1/tasks/missing-task-id",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    finally:
        _clear_overrides()


def test_update_task_quadrant(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        created = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={"title": "분류 변경 테스트"},
        )
        task_id = created.json()["id"]

        response = client.patch(
            f"/api/v1/tasks/{task_id}",
            headers=headers,
            json={"quadrant": "DELEGATE"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quadrant"] == "DELEGATE"
    finally:
        _clear_overrides()


def test_update_task_completed(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        created = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={"title": "완료 처리 테스트"},
        )
        task_id = created.json()["id"]

        response = client.patch(
            f"/api/v1/tasks/{task_id}",
            headers=headers,
            json={"completed": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
    finally:
        _clear_overrides()


def test_delete_task(client, auth_token, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        created = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={"title": "삭제 테스트"},
        )
        task_id = created.json()["id"]

        delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
        fetch_response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)

        assert delete_response.status_code == 204
        assert fetch_response.status_code == 404
    finally:
        _clear_overrides()


def test_tasks_require_auth(client, dynamodb_table, mock_ai_client):
    _override_dependencies(dynamodb_table, mock_ai_client)
    try:
        response = client.get("/api/v1/tasks")

        assert response.status_code == 401
    finally:
        _clear_overrides()
