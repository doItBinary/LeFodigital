from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings
from app.db.models import ActivityStatus, Evidence, User, UserRole
from app.dependencies import api_error
from app.modules.evidences.schemas import EvidenceMetadata
from app.modules.activities.service import get_activity
from app.modules.gamification.service import recalculate_medals
from app.storage.filesystem import FileSystemStorage


ALLOWED_FILE_TYPES = {
    ".png": {"image/png"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".gif": {"image/gif"},
    ".webp": {"image/webp"},
    ".pdf": {"application/pdf"},
    ".doc": {"application/msword"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
}


def sanitize_original_name(filename: str | None) -> str:
    basename = Path((filename or "evidence").replace("\\", "/")).name
    printable = "".join(
        character
        for character in basename
        if character.isprintable() and character not in {'"', "\r", "\n"}
    )
    return printable[:255] or "evidence"


def to_metadata(evidence: Evidence) -> EvidenceMetadata:
    return EvidenceMetadata(
        id=evidence.id,
        activity_id=evidence.activity_id,
        student_id=evidence.student_id,
        student_name=evidence.student.name,
        original_name=evidence.original_name,
        content_type=evidence.content_type,
        size_bytes=evidence.size_bytes,
        uploaded_at=evidence.uploaded_at,
    )


def upload_evidence(
    db: Session,
    student: User,
    activity_id: UUID,
    upload: UploadFile,
    settings: Settings,
) -> EvidenceMetadata:
    activity = get_activity(db, activity_id)
    if activity.status != ActivityStatus.PUBLISHED:
        raise api_error(status.HTTP_404_NOT_FOUND, "activity_not_available", "Actividad no disponible.")
    existing = db.scalar(
        select(Evidence).where(
            Evidence.activity_id == activity_id,
            Evidence.student_id == student.id,
        )
    )
    if existing:
        raise api_error(
            status.HTTP_409_CONFLICT,
            "evidence_already_exists",
            "Ya existe una evidencia para esta actividad.",
        )
    original_name = sanitize_original_name(upload.filename)
    suffix = Path(original_name).suffix.lower()
    content_type = upload.content_type or "application/octet-stream"
    if content_type not in ALLOWED_FILE_TYPES.get(suffix, set()):
        raise api_error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "unsupported_evidence_type",
            "El archivo debe ser una imagen, PDF, DOC o DOCX.",
        )
    content = upload.file.read(settings.max_upload_bytes + 1)
    if not content:
        raise api_error(status.HTTP_400_BAD_REQUEST, "empty_file", "El archivo está vacío.")
    if len(content) > settings.max_upload_bytes:
        raise api_error(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "evidence_too_large",
            "El archivo supera el límite de 1 MB.",
        )
    storage = FileSystemStorage(settings.evidence_storage_path)
    stored_name = storage.save(content, suffix)
    evidence = Evidence(
        activity_id=activity_id,
        student_id=student.id,
        original_name=original_name,
        stored_name=stored_name,
        content_type=content_type,
        size_bytes=len(content),
    )
    try:
        db.add(evidence)
        db.flush()
        recalculate_medals(db, student.id)
        db.commit()
        evidence = db.scalar(
            select(Evidence)
            .options(selectinload(Evidence.student))
            .where(Evidence.id == evidence.id)
        )
    except Exception:
        db.rollback()
        storage.delete(stored_name)
        raise
    return to_metadata(evidence)


def list_evidences(db: Session, activity_id: UUID) -> list[EvidenceMetadata]:
    get_activity(db, activity_id)
    items = db.scalars(
        select(Evidence)
        .options(selectinload(Evidence.student))
        .where(Evidence.activity_id == activity_id)
        .order_by(Evidence.uploaded_at.desc())
    ).all()
    return [to_metadata(item) for item in items]


def get_authorized_evidence(db: Session, user: User, evidence_id: UUID) -> Evidence:
    evidence = db.scalar(
        select(Evidence)
        .options(selectinload(Evidence.student))
        .where(Evidence.id == evidence_id)
    )
    if not evidence:
        raise api_error(status.HTTP_404_NOT_FOUND, "evidence_not_found", "Evidencia no encontrada.")
    if user.role != UserRole.TEACHER and evidence.student_id != user.id:
        raise api_error(
            status.HTTP_403_FORBIDDEN,
            "evidence_forbidden",
            "No puedes descargar esta evidencia.",
        )
    return evidence
