from datetime import datetime, timedelta, timezone
from importlib import import_module

import boto3
from moto import mock_aws

settings = import_module("app.core.config").settings
Task = import_module("app.models.task").Task
TaskRepository = import_module("app.repositories.task_repository").TaskRepository


def _create_table():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    create_table = getattr(dynamodb, "create_table")
    return create_table(
        TableName=settings.DYNAMODB_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            }
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )


def _make_task(
    *,
    task_id: str,
    user_id: str,
    title: str,
    quadrant: str = "DO",
    created_at: datetime | None = None,
):
    created = created_at or datetime.now(timezone.utc)
    return Task(
        id=task_id,
        user_id=user_id,
        title=title,
        quadrant=quadrant,
        urgency="urgent",
        importance="important",
        confidence=0.9,
        parsed_datetime=None,
        completed=False,
        created_at=created,
        updated_at=created,
    )


@mock_aws
def test_create_task():
    table = _create_table()
    repo = TaskRepository(table=table)
    task = _make_task(task_id="t1", user_id="u1", title="할 일 1")

    created = repo.create_task(task)

    assert created.id == "t1"
    assert created.title == "할 일 1"
    item = table.get_item(Key={"PK": "USER#u1", "SK": "TASK#t1"}).get("Item")
    assert item is not None
    assert item["title"] == "할 일 1"


@mock_aws
def test_get_task_exists():
    table = _create_table()
    repo = TaskRepository(table=table)
    task = _make_task(task_id="t1", user_id="u1", title="조회 테스트")
    repo.create_task(task)

    found = repo.get_task("u1", "t1")

    assert found is not None
    assert found.id == "t1"
    assert found.user_id == "u1"
    assert found.title == "조회 테스트"


@mock_aws
def test_get_task_not_found():
    table = _create_table()
    repo = TaskRepository(table=table)

    found = repo.get_task("u1", "missing")

    assert found is None


@mock_aws
def test_get_user_tasks_all():
    table = _create_table()
    repo = TaskRepository(table=table)
    repo.create_task(_make_task(task_id="t1", user_id="u1", title="u1 task 1"))
    repo.create_task(_make_task(task_id="t2", user_id="u1", title="u1 task 2", quadrant="DECIDE"))
    repo.create_task(_make_task(task_id="t3", user_id="u2", title="u2 task 1"))

    tasks = repo.get_user_tasks("u1")

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {"t1", "t2"}


@mock_aws
def test_get_user_tasks_by_quadrant():
    table = _create_table()
    repo = TaskRepository(table=table)
    now = datetime.now(timezone.utc)
    repo.create_task(
        _make_task(
            task_id="t1",
            user_id="u1",
            title="do first",
            quadrant="DO",
            created_at=now,
        )
    )
    repo.create_task(
        _make_task(
            task_id="t2",
            user_id="u1",
            title="delegate",
            quadrant="DELEGATE",
            created_at=now + timedelta(seconds=1),
        )
    )
    repo.create_task(
        _make_task(
            task_id="t3",
            user_id="u1",
            title="do second",
            quadrant="DO",
            created_at=now + timedelta(seconds=2),
        )
    )

    tasks = repo.get_user_tasks("u1", quadrant="DO")

    assert len(tasks) == 2
    assert [task.id for task in tasks] == ["t1", "t3"]
    assert all(task.quadrant == "DO" for task in tasks)


@mock_aws
def test_update_task():
    table = _create_table()
    repo = TaskRepository(table=table)
    now = datetime.now(timezone.utc)
    task = _make_task(task_id="t1", user_id="u1", title="before", created_at=now)
    repo.create_task(task)

    updated_task = Task(
        id="t1",
        user_id="u1",
        title="after",
        quadrant="DO",
        urgency="urgent",
        importance="important",
        confidence=0.95,
        parsed_datetime=None,
        completed=True,
        created_at=now,
        updated_at=now + timedelta(minutes=1),
    )
    updated = repo.update_task(updated_task)
    found = repo.get_task("u1", "t1")

    assert updated.title == "after"
    assert found is not None
    assert found.title == "after"
    assert found.completed is True
    assert found.confidence == 0.95


@mock_aws
def test_delete_task():
    table = _create_table()
    repo = TaskRepository(table=table)
    repo.create_task(_make_task(task_id="t1", user_id="u1", title="delete me"))

    repo.delete_task("u1", "t1")

    found = repo.get_task("u1", "t1")
    assert found is None


def test_to_item_and_back():
    repo = TaskRepository.__new__(TaskRepository)
    now = datetime.now(timezone.utc)
    task = Task(
        id="t1",
        user_id="u1",
        title="테스트",
        quadrant="DO",
        urgency="urgent",
        importance="important",
        confidence=0.9,
        parsed_datetime=None,
        completed=False,
        created_at=now,
        updated_at=now,
    )

    item = repo._to_item(task)
    back = repo._to_entity(item)

    assert item["PK"] == "USER#u1"
    assert item["SK"] == "TASK#t1"
    assert item["GSI1PK"] == "USER#u1"
    assert item["GSI1SK"].startswith("QUADRANT#DO#DATE#")
    assert back.id == task.id
    assert back.user_id == task.user_id
    assert back.title == task.title
    assert back.quadrant == task.quadrant
    assert back.urgency == task.urgency
    assert back.importance == task.importance
    assert back.completed == task.completed
    assert back.created_at == task.created_at
    assert back.updated_at == task.updated_at
