from datetime import datetime

from app.core.schemas import ApiModel


class MedalDefinition(ApiModel):
    key: str
    icon: str
    name: str
    description: str


class EarnedMedal(MedalDefinition):
    awarded_at: datetime


class GamificationProgress(ApiModel):
    points: int
    level: int
    completed_activities: int
    medals: list[EarnedMedal]
    points_in_level: int
