from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import User, UserRole
from app.db.session import get_db
from app.dependencies import require_role
from app.modules.reports.schemas import StudentReport, TeacherReport
from app.modules.reports.service import student_report, teacher_report


router = APIRouter(prefix="/reports", tags=["Reportes"])


@router.get("/student/me", response_model=StudentReport)
def get_student_report(
    student: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
) -> StudentReport:
    return student_report(db, student)


@router.get("/teacher", response_model=TeacherReport)
def get_teacher_report(
    _: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
) -> TeacherReport:
    return teacher_report(db)
