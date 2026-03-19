import json
from datetime import datetime
from importlib import import_module
from unittest.mock import MagicMock

AIService = import_module("app.services.ai_service").AIService


def _mock_chat_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content))]
    return response


def test_classify_task_success(mock_ai_client: MagicMock):
    payload = {
        "urgency": "urgent",
        "importance": "important",
        "confidence": 0.92,
        "reasoning": "오늘 마감이고 핵심 업무입니다.",
        "parsed_datetime": "2026-03-20T15:00:00",
    }
    mock_ai_client.chat.completions.create.side_effect = None
    mock_ai_client.chat.completions.create.return_value = _mock_chat_response(
        f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"
    )

    service = AIService(client=mock_ai_client)
    result = service.classify_task("오늘 3시까지 보고서 제출")

    assert result.urgency == "urgent"
    assert result.importance == "important"
    assert result.confidence == 0.92
    assert result.reasoning == "오늘 마감이고 핵심 업무입니다."
    assert getattr(result, "quadrant") == "DO"


def test_classify_task_with_datetime(mock_ai_client: MagicMock):
    payload = {
        "urgency": "not-urgent",
        "importance": "important",
        "confidence": 0.8,
        "reasoning": "다음 주 목표에 중요합니다.",
        "parsed_datetime": "2026-03-27T10:30:00",
    }
    mock_ai_client.chat.completions.create.side_effect = None
    mock_ai_client.chat.completions.create.return_value = _mock_chat_response(
        json.dumps(payload, ensure_ascii=False)
    )

    service = AIService(client=mock_ai_client)
    result = service.classify_task("다음 주 금요일 팀미팅 준비")

    assert isinstance(result.parsed_datetime, datetime)
    assert result.parsed_datetime == datetime.fromisoformat("2026-03-27T10:30:00")
    assert getattr(result, "quadrant") == "PLAN"


def test_classify_task_no_datetime(mock_ai_client: MagicMock):
    payload = {
        "urgency": "urgent",
        "importance": "not-important",
        "confidence": 0.75,
        "reasoning": "긴급하지만 위임 가능한 업무입니다.",
        "parsed_datetime": None,
    }
    mock_ai_client.chat.completions.create.side_effect = None
    mock_ai_client.chat.completions.create.return_value = _mock_chat_response(
        json.dumps(payload, ensure_ascii=False)
    )

    service = AIService(client=mock_ai_client)
    result = service.classify_task("오늘 안에 택배 발송 요청")

    assert result.parsed_datetime is None
    assert result.urgency == "urgent"
    assert result.importance == "not-important"
    assert getattr(result, "quadrant") == "DELEGATE"


def test_classify_task_malformed_json(mock_ai_client: MagicMock):
    mock_ai_client.chat.completions.create.side_effect = None
    mock_ai_client.chat.completions.create.return_value = _mock_chat_response(
        "{invalid-json}"
    )

    service = AIService(client=mock_ai_client)
    result = service.classify_task("언젠가 책 정리")

    assert result.urgency is None
    assert result.importance is None
    assert result.confidence == 0
    assert result.reasoning == "파싱 실패"
    assert result.parsed_datetime is None
    assert getattr(result, "quadrant") is None


def test_classify_task_timeout(mock_ai_client: MagicMock):
    mock_ai_client.chat.completions.create.side_effect = TimeoutError("timeout")

    service = AIService(client=mock_ai_client)
    result = service.classify_task("오늘 자정까지 과제 제출")

    assert result.urgency is None
    assert result.importance is None
    assert result.confidence == 0
    assert result.reasoning == "파싱 실패"
    assert result.parsed_datetime is None
    assert getattr(result, "quadrant") is None


def test_quadrant_mapping():
    assert AIService._determine_quadrant("urgent", "important") == "DO"
    assert AIService._determine_quadrant("not-urgent", "important") == "PLAN"
    assert AIService._determine_quadrant("urgent", "not-important") == "DELEGATE"
    assert (
        AIService._determine_quadrant("not-urgent", "not-important") == "ELIMINATE"
    )
