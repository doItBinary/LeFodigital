from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.models import User, UserRole
from app.db.session import get_db
from app.dependencies import get_current_user, require_role
from app.modules.activities.schemas import (
    ActivitySummary,
    CompletionResponse,
    CreateActivityRequest,
)
from app.modules.activities.service import (
    complete_activity,
    create_activity,
    delete_activity,
    list_activities,
    publish_activity,
)
from app.storage.filesystem import FileSystemStorage


router = APIRouter(prefix="/activities", tags=["Actividades"])


@router.get("", response_model=list[ActivitySummary])
def get_activities(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActivitySummary]:
    return list_activities(db, user)


@router.post("", response_model=ActivitySummary, status_code=status.HTTP_201_CREATED)
def post_activity(
    data: CreateActivityRequest,
    teacher: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
) -> ActivitySummary:
    return create_activity(db, teacher, data)


@router.post("/{activity_id}/publish", response_model=ActivitySummary)
def publish(
    activity_id: UUID,
    teacher: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
) -> ActivitySummary:
    return publish_activity(db, teacher, activity_id)


@router.post("/{activity_id}/complete", response_model=CompletionResponse)
def complete(
    activity_id: UUID,
    student: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
) -> CompletionResponse:
    activity = complete_activity(db, student, activity_id)
    return CompletionResponse(message="Actividad completada.", activity=activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    activity_id: UUID,
    _: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    delete_activity(db, activity_id, FileSystemStorage(settings.evidence_storage_path))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
