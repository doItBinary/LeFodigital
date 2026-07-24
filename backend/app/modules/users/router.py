from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.modules.users.schemas import UpdateProfileRequest, UserProfile
from app.modules.users.service import update_profile as update_user_profile


router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserProfile)
def get_profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserProfile)
def update_profile(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return update_user_profile(db, user, data)
