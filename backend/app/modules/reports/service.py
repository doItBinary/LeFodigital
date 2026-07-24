from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Activity, ActivityStatus, Evidence, User, UserRole
from app.modules.activities.service import list_activities
from app.modules.gamification.service import get_progress
from app.modules.reports.schemas import (
    StudentReport,
    TeacherReport,
    TeacherStudentReport,
)


def student_report(db: Session, student: User) -> StudentReport:
    progress = get_progress(db, student.id)
    activities = list_activities(db, student)
    return StudentReport(
        student_id=student.id,
        name=student.name,
        email=student.email,
        institution=student.institution,
        progress=progress,
        total_published_activities=len(activities),
        completed=[item for item in activities if item.completed],
    )


def teacher_report(db: Session) -> TeacherReport:
    students = db.scalars(
        select(User)
        .where(User.role == UserRole.STUDENT)
        .order_by(User.name.asc())
    ).all()
    total_activities = int(
        db.scalar(
            select(func.count(Activity.id)).where(
                Activity.status == ActivityStatus.PUBLISHED
            )
        )
        or 0
    )
    rows: list[TeacherStudentReport] = []
    for student in students:
        progress = get_progress(db, student.id)
        evidence_count = int(
            db.scalar(
                select(func.count(Evidence.id)).where(Evidence.student_id == student.id)
            )
            or 0
        )
        percent = (
            round(progress.completed_activities / total_activities * 100)
            if total_activities
            else 0
        )
        rows.append(
            TeacherStudentReport(
                student_id=student.id,
                name=student.name,
                email=student.email,
                institution=student.institution,
                progress=progress,
                total_published_activities=total_activities,
                progress_percent=percent,
                evidence_count=evidence_count,
            )
        )
    count = len(rows)
    return TeacherReport(
        students=rows,
        total_students=count,
        total_published_activities=total_activities,
        average_points=round(sum(row.progress.points for row in rows) / count) if count else 0,
        average_level=round(sum(row.progress.level for row in rows) / count, 1) if count else 0,
        total_medals=sum(len(row.progress.medals) for row in rows),
    )
