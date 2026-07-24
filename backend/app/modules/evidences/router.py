from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.models import User, UserRole
from app.db.session import get_db
from app.dependencies import get_current_user, require_role
from app.modules.evidences.schemas import EvidenceMetadata
from app.modules.evidences.service import (
    get_authorized_evidence,
    list_evidences,
    upload_evidence,
)
from app.storage.filesystem import FileSystemStorage


activity_router = APIRouter(prefix="/activities", tags=["Evidencias"])
router = APIRouter(prefix="/evidences", tags=["Evidencias"])


@activity_router.post("/{activity_id}/evidence", response_model=EvidenceMetadata)
def upload(
    activity_id: UUID,
    file: UploadFile = File(...),
    student: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> EvidenceMetadata:
    return upload_evidence(db, student, activity_id, file, settings)


@activity_router.get("/{activity_id}/evidences", response_model=list[EvidenceMetadata])
def get_all(
    activity_id: UUID,
    _: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
) -> list[EvidenceMetadata]:
    return list_evidences(db, activity_id)


@router.get("/{evidence_id}/download")
def download(
    evidence_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    evidence = get_authorized_evidence(db, user, evidence_id)
    path = FileSystemStorage(settings.evidence_storage_path).path_for(evidence.stored_name)
    return FileResponse(
        path,
        media_type=evidence.content_type,
        filename=evidence.original_name,
    )
