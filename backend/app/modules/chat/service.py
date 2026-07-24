from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from threading import Lock

from fastapi import status
from openai import AsyncOpenAI, OpenAIError

from app.core.config import Settings
from app.dependencies import api_error
from app.modules.chat.schemas import ChatMessage


INSTRUCTIONS = """You are LeFoBot, a friendly and professional educational assistant.
Help students and teachers with academic questions, study strategies and use of
LeFodigital. Always answer in Spanish, clearly and concisely, in no more than
three short paragraphs. Do not claim to have performed actions in the platform."""


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int) -> bool:
        now = datetime.now(UTC)
        cutoff = now - timedelta(minutes=1)
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] < cutoff:
                requests.popleft()
            if len(requests) >= limit:
                return False
            requests.append(now)
            return True


rate_limiter = InMemoryRateLimiter()


async def ask_lefobot(messages: list[ChatMessage], settings: Settings) -> str:
    if not settings.openai_api_key:
        raise api_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "chat_not_configured",
            "LeFoBot no está configurado en este ambiente.",
        )
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=INSTRUCTIONS,
            input=[
                {"role": message.role, "content": message.content}
                for message in messages[-10:]
            ],
            max_output_tokens=700,
        )
    except OpenAIError:
        raise api_error(
            status.HTTP_502_BAD_GATEWAY,
            "chat_provider_error",
            "LeFoBot no está disponible en este momento. Intenta más tarde.",
        ) from None
    answer = (response.output_text or "").strip()
    return answer or "No pude generar una respuesta. Intenta nuevamente."
