from fastapi import APIRouter, Depends, Request, status

from app.core.config import Settings, get_settings
from app.dependencies import api_error, get_client_ip
from app.modules.chat.schemas import ChatRequest, ChatResponse
from app.modules.chat.service import ask_lefobot, rate_limiter


router = APIRouter(prefix="/chat", tags=["LeFoBot"])


@router.post("/messages", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    if not rate_limiter.check(
        get_client_ip(request), settings.chat_rate_limit_per_minute
    ):
        raise api_error(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "chat_rate_limited",
            "Has enviado demasiadas solicitudes. Espera un minuto.",
        )
    answer = await ask_lefobot(data.messages, settings)
    return ChatResponse(message=answer)
