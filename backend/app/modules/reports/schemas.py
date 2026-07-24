from uuid import UUID

from app.core.schemas import ApiModel
from app.modules.activities.schemas import ActivitySummary
from app.modules.gamification.schemas import GamificationProgress


class StudentReport(ApiModel):
    student_id: UUID
    name: str
    email: str
    institution: str
    progress: GamificationProgress
    total_published_activities: int
    completed: list[ActivitySummary]


class TeacherStudentReport(ApiModel):
    student_id: UUID
    name: str
    email: str
    institution: str
    progress: GamificationProgress
    total_published_activities: int
    progress_percent: int
    evidence_count: int


class TeacherReport(ApiModel):
    students: list[TeacherStudentReport]
    total_students: int
    total_published_activities: int
    average_points: int
    average_level: float
    total_medals: int
