from typing import Literal

from pydantic import Field

from app.core.schemas import ApiModel


class ChatMessage(ApiModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=400)


class ChatRequest(ApiModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=10)


class ChatResponse(ApiModel):
    message: str
