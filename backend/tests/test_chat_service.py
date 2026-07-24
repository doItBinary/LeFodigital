import asyncio
from types import SimpleNamespace

from fastapi import HTTPException
from openai import OpenAIError
import pytest

from app.modules.chat import service
from app.modules.chat.schemas import ChatMessage


def test_openai_adapter_limits_context_and_output(monkeypatch, settings) -> None:
    captured: dict = {}

    class FakeResponses:
        async def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text="Respuesta educativa.")

    class FakeClient:
        def __init__(self, api_key: str):
            captured["api_key"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setattr(service, "AsyncOpenAI", FakeClient)
    settings.openai_api_key = "test-key"
    messages = [
        ChatMessage(role="user", content=f"Pregunta {index}")
        for index in range(12)
    ]

    answer = asyncio.run(service.ask_lefobot(messages, settings))

    assert answer == "Respuesta educativa."
    assert captured["api_key"] == "test-key"
    assert len(captured["input"]) == 10
    assert captured["max_output_tokens"] == 700


def test_openai_adapter_hides_provider_failure(monkeypatch, settings) -> None:
    class FailingResponses:
        async def create(self, **_):
            raise OpenAIError("provider details")

    class FailingClient:
        def __init__(self, api_key: str):
            self.responses = FailingResponses()

    monkeypatch.setattr(service, "AsyncOpenAI", FailingClient)
    settings.openai_api_key = "test-key"

    with pytest.raises(HTTPException) as raised:
        asyncio.run(
            service.ask_lefobot(
                [ChatMessage(role="user", content="Hola")],
                settings,
            )
        )

    assert raised.value.status_code == 502
    assert raised.value.detail["code"] == "chat_provider_error"
    assert "provider details" not in raised.value.detail["message"]


def test_rate_limiter_rejects_excess_requests() -> None:
    limiter = service.InMemoryRateLimiter()

    assert limiter.check("127.0.0.1", 1)
    assert not limiter.check("127.0.0.1", 1)
    assert limiter.check("127.0.0.2", 1)
