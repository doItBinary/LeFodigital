from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.core.schemas import ApiModel
from app.db.models import UserRole


class UserProfile(ApiModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    institution: str
    created_at: datetime


class UpdateProfileRequest(ApiModel):
    name: str = Field(min_length=2, max_length=120)
    institution: str = Field(default="", max_length=160)
