from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import User, UserRole
from app.db.session import get_db
from app.dependencies import get_current_user, require_role
from app.modules.courses.schemas import CourseSummary, CreateCourseRequest
from app.modules.courses.service import create_course, list_courses


router = APIRouter(prefix="/courses", tags=["Cursos"])


@router.get("", response_model=list[CourseSummary])
def get_courses(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CourseSummary]:
    return list_courses(db)


@router.post("", response_model=CourseSummary, status_code=status.HTTP_201_CREATED)
def post_course(
    data: CreateCourseRequest,
    teacher: User = Depends(require_role(UserRole.TEACHER)),
    db: Session = Depends(get_db),
) -> CourseSummary:
    return create_course(db, teacher, data)
