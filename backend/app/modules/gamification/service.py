from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import ActivityCompletion, Evidence, Post, UserMedal
from app.modules.gamification.schemas import (
    EarnedMedal,
    GamificationProgress,
    MedalDefinition,
)


@dataclass(frozen=True)
class MedalRule:
    key: str
    icon: str
    name: str
    description: str
    completed: int = 0
    points: int = 0
    requires_post: bool = False
    requires_evidence: bool = False


MEDALS = (
    MedalRule("first_task", "🥉", "Primera tarea", "Completa tu primera actividad", completed=1),
    MedalRule("five_tasks", "🥈", "Estudiante activo", "Completa 5 actividades", completed=5),
    MedalRule("ten_tasks", "🥇", "Experto", "Completa 10 actividades", completed=10),
    MedalRule("points_50", "⭐", "Primeros 50 pts", "Acumula 50 puntos", points=50),
    MedalRule("points_100", "🏆", "Centenario", "Alcanza 100 puntos", points=100),
    MedalRule("points_500", "👑", "Maestro", "Alcanza 500 puntos", points=500),
    MedalRule("blogger", "✍️", "Blogger", "Publica tu primera entrada en blog", requires_post=True),
    MedalRule(
        "first_evidence",
        "📎",
        "Documentado",
        "Sube tu primera evidencia",
        requires_evidence=True,
    ),
)


def medal_definitions() -> list[MedalDefinition]:
    return [
        MedalDefinition(
            key=rule.key,
            icon=rule.icon,
            name=rule.name,
            description=rule.description,
        )
        for rule in MEDALS
    ]


def _metrics(db: Session, user_id: UUID) -> tuple[int, int, bool, bool]:
    points = db.scalar(
        select(func.coalesce(func.sum(ActivityCompletion.awarded_points), 0)).where(
            ActivityCompletion.student_id == user_id
        )
    )
    completed = db.scalar(
        select(func.count(ActivityCompletion.id)).where(
            ActivityCompletion.student_id == user_id
        )
    )
    has_post = bool(
        db.scalar(select(func.count(Post.id)).where(Post.author_id == user_id))
    )
    has_evidence = bool(
        db.scalar(select(func.count(Evidence.id)).where(Evidence.student_id == user_id))
    )
    return int(points or 0), int(completed or 0), has_post, has_evidence


def recalculate_medals(db: Session, user_id: UUID) -> None:
    points, completed, has_post, has_evidence = _metrics(db, user_id)
    earned_keys = {
        rule.key
        for rule in MEDALS
        if (not rule.completed or completed >= rule.completed)
        and (not rule.points or points >= rule.points)
        and (not rule.requires_post or has_post)
        and (not rule.requires_evidence or has_evidence)
    }
    current = {
        medal.medal_key: medal
        for medal in db.scalars(select(UserMedal).where(UserMedal.user_id == user_id))
    }
    for key in earned_keys - current.keys():
        db.add(UserMedal(user_id=user_id, medal_key=key))
    obsolete = current.keys() - earned_keys
    if obsolete:
        db.execute(
            delete(UserMedal).where(
                UserMedal.user_id == user_id,
                UserMedal.medal_key.in_(obsolete),
            )
        )


def get_progress(db: Session, user_id: UUID) -> GamificationProgress:
    points, completed, _, _ = _metrics(db, user_id)
    awarded = {
        item.medal_key: item.awarded_at
        for item in db.scalars(
            select(UserMedal).where(UserMedal.user_id == user_id)
        )
    }
    medals = [
        EarnedMedal(
            key=rule.key,
            icon=rule.icon,
            name=rule.name,
            description=rule.description,
            awarded_at=awarded[rule.key],
        )
        for rule in MEDALS
        if rule.key in awarded
    ]
    return GamificationProgress(
        points=points,
        level=max(1, points // 100 + 1),
        completed_activities=completed,
        medals=medals,
        points_in_level=points % 100,
    )
