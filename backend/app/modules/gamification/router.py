from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.gamification.schemas import GamificationProgress, MedalDefinition
from app.modules.gamification.service import get_progress, medal_definitions


router = APIRouter(prefix="/gamification", tags=["Gamificación"])


@router.get("/me", response_model=GamificationProgress)
def progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GamificationProgress:
    return get_progress(db, user.id)


@router.get("/medals", response_model=list[MedalDefinition])
def medals(_: User = Depends(get_current_user)) -> list[MedalDefinition]:
    return medal_definitions()
