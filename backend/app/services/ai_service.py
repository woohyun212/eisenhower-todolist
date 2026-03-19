import json
import re
from typing import Any

from openai import APITimeoutError, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..core.config import settings
from ..schemas.task import AIClassification


class AIService:
    _DEFAULT_MODEL = "Qwen/Qwen3.5-9B"

    def __init__(self, client: OpenAI | Any | None = None) -> None:
        self.model = getattr(settings, "AI_MODEL", self._DEFAULT_MODEL)
        if self.model == "gpt-3.5-turbo":
            self.model = self._DEFAULT_MODEL

        api_key = settings.AI_API_KEY
        self.client = client or OpenAI(
            base_url=settings.AI_BASE_URL,
            api_key=api_key,
            timeout=float(settings.AI_TIMEOUT),
        )

    def classify_task(self, title: str) -> AIClassification:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_prompt(title),
                temperature=0.3,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                    "top_k": 20,
                },
            )
            content = (response.choices[0].message.content or "").strip()
            classification = self._parse_response(content)
            quadrant = self._determine_quadrant(
                classification.urgency,
                classification.importance,
            )
            object.__setattr__(classification, "quadrant", quadrant)
            return classification
        except (APITimeoutError, TimeoutError):
            return self._fallback("파싱 실패")
        except Exception:
            return self._fallback("파싱 실패")

    def _build_prompt(self, title: str) -> list[ChatCompletionMessageParam]:
        from datetime import datetime, timezone, timedelta
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst).strftime("%Y-%m-%d %H:%M (%A)")
        system_prompt = (
            f"현재 날짜/시간: {now} (KST)\n"
            "너는 할 일 우선순위 분류 도우미야. 아이젠하워 매트릭스를 사용해.\n"
            "- 긴급(urgent): 48시간 이내 마감, 다른 작업을 차단, 외부 시간 압박\n"
            "- 중요(important): 장기 목표와 연관, 큰 결과를 초래, 깊은 작업 필요\n"
            "반드시 raw JSON으로만 응답해 (마크다운 코드 블록 없이): "
            "{urgency, importance, confidence, reasoning, parsed_datetime}\n"
            "parsed_datetime은 반드시 현재 날짜 기준으로 계산해. "
            "예: '내일 3시' → 현재 날짜 + 1일의 15:00, '12시 30분' → 오늘 12:30"
        )
        user_prompt = f"다음 할 일을 분류해줘: '{title}'"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _parse_response(self, content: str) -> AIClassification:
        response_text = content.strip()
        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            response_text,
            re.DOTALL,
        )
        if json_match:
            response_text = json_match.group(1)

        try:
            parsed = json.loads(response_text)
            return AIClassification.model_validate(parsed)
        except Exception:
            return self._fallback("파싱 실패")

    @staticmethod
    def _is_high(value: str | None) -> bool:
        if not value:
            return False
        v = value.lower().strip()
        return v in ("high", "urgent", "important", "긴급", "중요")

    @staticmethod
    def _determine_quadrant(
        urgency: str | None,
        importance: str | None,
    ) -> str | None:
        if urgency is None and importance is None:
            return None
        u = AIService._is_high(urgency)
        i = AIService._is_high(importance)
        if u and i:
            return "DO"
        if not u and i:
            return "PLAN"
        if u and not i:
            return "DELEGATE"
        return "ELIMINATE"

    @classmethod
    def _fallback(cls, reasoning: str) -> AIClassification:
        fallback = AIClassification(
            urgency=None,
            importance=None,
            confidence=0,
            reasoning=reasoning,
            parsed_datetime=None,
        )
        object.__setattr__(fallback, "quadrant", None)
        return fallback
