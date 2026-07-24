from pydantic import EmailStr, Field

from app.core.schemas import ApiModel
from app.db.models import UserRole
from app.modules.users.schemas import UserProfile


class RegisterRequest(ApiModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    teacher_invitation_code: str | None = Field(default=None, max_length=128)


class LoginRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthSession(ApiModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class RegisterResponse(ApiModel):
    message: str
    user: UserProfile
