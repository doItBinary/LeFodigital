from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.core.schemas import ApiModel


class CreateCourseRequest(ApiModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=3000)


class CourseSummary(ApiModel):
    id: UUID
    name: str
    description: str
    owner_id: UUID
    owner_name: str
    created_at: datetime
