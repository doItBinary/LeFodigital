from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.health.schemas import LiveHealth, ReadyHealth
from app.modules.health.service import get_live_status, get_ready_status


router = APIRouter(prefix="/health", tags=["Salud"])


@router.get("/live", response_model=LiveHealth)
def live() -> LiveHealth:
    return get_live_status()


@router.get("/ready", response_model=ReadyHealth)
def ready(db: Session = Depends(get_db)) -> ReadyHealth:
    return get_ready_status(db)
