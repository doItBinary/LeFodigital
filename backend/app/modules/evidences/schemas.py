from datetime import datetime
from uuid import UUID

from app.core.schemas import ApiModel


class EvidenceMetadata(ApiModel):
    id: UUID
    activity_id: UUID
    student_id: UUID
    student_name: str
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime
