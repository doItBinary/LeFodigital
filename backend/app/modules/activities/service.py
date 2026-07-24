from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    Activity,
    ActivityCompletion,
    ActivityStatus,
    Course,
    Evidence,
    User,
    UserRole,
)
from app.dependencies import api_error
from app.modules.activities.schemas import (
    ActivitySummary,
    CreateActivityRequest,
)
from app.modules.evidences.schemas import EvidenceMetadata
from app.modules.gamification.service import recalculate_medals
from app.storage.filesystem import FileSystemStorage


logger = logging.getLogger(__name__)


def _query():
    return select(Activity).options(
        selectinload(Activity.author),
        selectinload(Activity.course),
        selectinload(Activity.completions),
        selectinload(Activity.evidences).selectinload(Evidence.student),
    )


def _evidence_metadata(item) -> EvidenceMetadata:
    return EvidenceMetadata(
        id=item.id,
        activity_id=item.activity_id,
        student_id=item.student_id,
        student_name=item.student.name,
        original_name=item.original_name,
        content_type=item.content_type,
        size_bytes=item.size_bytes,
        uploaded_at=item.uploaded_at,
    )


def to_summary(activity: Activity, user: User) -> ActivitySummary:
    completion = next(
        (item for item in activity.completions if item.student_id == user.id), None
    )
    evidence = next(
        (item for item in activity.evidences if item.student_id == user.id), None
    )
    return ActivitySummary(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        points=activity.points,
        due_date=activity.due_date,
        status=activity.status,
        course_id=activity.course_id,
        course_name=activity.course.name if activity.course else None,
        author_name=activity.author.name,
        created_at=activity.created_at,
        published_at=activity.published_at,
        completed=completion is not None,
        completion_count=len(activity.completions),
        evidence_count=len(activity.evidences),
        my_evidence=_evidence_metadata(evidence) if evidence else None,
    )


def get_activity(db: Session, activity_id: UUID) -> Activity:
    activity = db.scalar(_query().where(Activity.id == activity_id))
    if not activity:
        raise api_error(status.HTTP_404_NOT_FOUND, "activity_not_found", "Actividad no encontrada.")
    return activity


def list_activities(db: Session, user: User) -> list[ActivitySummary]:
    statement = _query().order_by(Activity.created_at.desc())
    if user.role == UserRole.STUDENT:
        statement = statement.where(Activity.status == ActivityStatus.PUBLISHED)
    return [to_summary(item, user) for item in db.scalars(statement).unique().all()]


def create_activity(
    db: Session,
    teacher: User,
    data: CreateActivityRequest,
) -> ActivitySummary:
    if data.course_id and not db.get(Course, data.course_id):
        raise api_error(status.HTTP_400_BAD_REQUEST, "invalid_course", "El curso no existe.")
    activity = Activity(
        title=data.title.strip(),
        description=data.description.strip(),
        points=data.points,
        due_date=data.due_date,
        course_id=data.course_id,
        author_id=teacher.id,
        status=ActivityStatus.DRAFT,
    )
    db.add(activity)
    db.commit()
    return to_summary(get_activity(db, activity.id), teacher)


def publish_activity(db: Session, teacher: User, activity_id: UUID) -> ActivitySummary:
    activity = get_activity(db, activity_id)
    if activity.status != ActivityStatus.PUBLISHED:
        activity.status = ActivityStatus.PUBLISHED
        activity.published_at = datetime.now(UTC)
        db.commit()
        activity = get_activity(db, activity_id)
    return to_summary(activity, teacher)


def complete_activity(db: Session, student: User, activity_id: UUID) -> ActivitySummary:
    activity = get_activity(db, activity_id)
    if activity.status != ActivityStatus.PUBLISHED:
        raise api_error(
            status.HTTP_404_NOT_FOUND,
            "activity_not_available",
            "La actividad no está disponible.",
        )
    existing = db.scalar(
        select(ActivityCompletion).where(
            ActivityCompletion.activity_id == activity.id,
            ActivityCompletion.student_id == student.id,
        )
    )
    if not existing:
        db.add(
            ActivityCompletion(
                activity_id=activity.id,
                student_id=student.id,
                awarded_points=activity.points,
            )
        )
        db.flush()
        recalculate_medals(db, student.id)
        db.commit()
        db.expire_all()
    return to_summary(get_activity(db, activity_id), student)


def delete_activity(
    db: Session,
    activity_id: UUID,
    storage: FileSystemStorage,
) -> None:
    activity = get_activity(db, activity_id)
    student_ids = {item.student_id for item in activity.completions}
    student_ids.update(item.student_id for item in activity.evidences)
    stored_names = [item.stored_name for item in activity.evidences]
    db.delete(activity)
    db.flush()
    for student_id in student_ids:
        recalculate_medals(db, student_id)
    db.commit()
    for stored_name in stored_names:
        try:
            storage.delete(stored_name)
        except OSError:
            logger.exception("Unable to remove evidence file %s", stored_name)
