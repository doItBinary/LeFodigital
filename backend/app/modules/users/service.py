from sqlalchemy.orm import Session

from app.db.models import User
from app.modules.users.schemas import UpdateProfileRequest


def update_profile(
    db: Session,
    user: User,
    data: UpdateProfileRequest,
) -> User:
    user.name = data.name.strip()
    user.institution = data.institution.strip()
    db.commit()
    db.refresh(user)
    return user
