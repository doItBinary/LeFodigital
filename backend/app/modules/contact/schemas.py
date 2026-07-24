from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.core.schemas import ApiModel


class CreateContactMessageRequest(ApiModel):
    subject: str = Field(min_length=2, max_length=180)
    message: str = Field(min_length=2, max_length=5000)


class ContactMessageResponse(ApiModel):
    id: UUID
    subject: str
    message: str
    created_at: datetime
