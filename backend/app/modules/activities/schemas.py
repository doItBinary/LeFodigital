from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from app.core.schemas import ApiModel
from app.db.models import ActivityStatus
from app.modules.evidences.schemas import EvidenceMetadata


class CreateActivityRequest(ApiModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=5000)
    points: int = Field(ge=1, le=10_000)
    due_date: date | None = None
    course_id: UUID | None = None


class ActivitySummary(ApiModel):
    id: UUID
    title: str
    description: str
    points: int
    due_date: date | None
    status: ActivityStatus
    course_id: UUID | None
    course_name: str | None
    author_name: str
    created_at: datetime
    published_at: datetime | None
    completed: bool
    completion_count: int
    evidence_count: int
    my_evidence: EvidenceMetadata | None


class CompletionResponse(ApiModel):
    message: str
    activity: ActivitySummary
