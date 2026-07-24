from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.health.schemas import LiveHealth, ReadyHealth


def get_live_status() -> LiveHealth:
    return LiveHealth(status="ok")


def get_ready_status(db: Session) -> ReadyHealth:
    db.execute(text("SELECT 1"))
    return ReadyHealth(status="ready")
