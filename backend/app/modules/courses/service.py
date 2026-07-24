from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Course, User
from app.modules.courses.schemas import CourseSummary, CreateCourseRequest


def to_summary(course: Course) -> CourseSummary:
    return CourseSummary(
        id=course.id,
        name=course.name,
        description=course.description,
        owner_id=course.owner_id,
        owner_name=course.owner.name,
        created_at=course.created_at,
    )


def list_courses(db: Session) -> list[CourseSummary]:
    courses = db.scalars(
        select(Course).options(joinedload(Course.owner)).order_by(Course.created_at.desc())
    ).all()
    return [to_summary(course) for course in courses]


def create_course(db: Session, user: User, data: CreateCourseRequest) -> CourseSummary:
    course = Course(
        name=data.name.strip(),
        description=data.description.strip(),
        owner_id=user.id,
    )
    db.add(course)
    db.commit()
    course = db.scalar(
        select(Course).options(joinedload(Course.owner)).where(Course.id == course.id)
    )
    return to_summary(course)
