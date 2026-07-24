from datetime import UTC, datetime
import secrets
from uuid import UUID

import jwt
from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.db.models import RefreshSession, User, UserRole
from app.dependencies import api_error
from app.modules.auth.schemas import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    def register(self, data: RegisterRequest) -> User:
        email = data.email.lower()
        existing = self.db.scalar(select(User).where(func.lower(User.email) == email))
        if existing:
            raise api_error(
                status.HTTP_409_CONFLICT,
                "email_already_registered",
                "Ya existe una cuenta con ese correo.",
            )
        if data.role == UserRole.TEACHER:
            provided = data.teacher_invitation_code or ""
            expected = self.settings.teacher_invitation_code
            if not expected or not secrets.compare_digest(provided, expected):
                raise api_error(
                    status.HTTP_403_FORBIDDEN,
                    "invalid_teacher_invitation",
                    "El código de invitación docente no es válido.",
                )
        user = User(
            name=data.name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, data: LoginRequest) -> User:
        user = self.db.scalar(
            select(User).where(func.lower(User.email) == data.email.lower())
        )
        if not user or not verify_password(data.password, user.password_hash):
            raise api_error(
                status.HTTP_401_UNAUTHORIZED,
                "invalid_credentials",
                "Correo o contraseña incorrectos.",
            )
        if not user.is_active:
            raise api_error(
                status.HTTP_403_FORBIDDEN,
                "inactive_user",
                "La cuenta está deshabilitada.",
            )
        return user

    def create_session(self, user: User) -> tuple[str, str]:
        access_token, _, _ = create_token(user.id, "access", self.settings)
        refresh_token, refresh_id, expires_at = create_token(
            user.id, "refresh", self.settings
        )
        self.db.add(
            RefreshSession(
                id=refresh_id,
                user_id=user.id,
                expires_at=expires_at,
            )
        )
        self.db.commit()
        return access_token, refresh_token

    def rotate_session(self, refresh_token: str) -> tuple[User, str, str]:
        try:
            payload = decode_token(refresh_token, "refresh", self.settings)
            session_id = UUID(payload["jti"])
            user_id = UUID(payload["sub"])
        except (jwt.InvalidTokenError, KeyError, ValueError):
            raise api_error(
                status.HTTP_401_UNAUTHORIZED,
                "invalid_refresh_token",
                "La sesión no se puede renovar.",
            ) from None
        current = self.db.get(RefreshSession, session_id)
        now = datetime.now(UTC)
        current_expiration = current.expires_at if current else now
        if current_expiration.tzinfo is None:
            current_expiration = current_expiration.replace(tzinfo=UTC)
        if (
            not current
            or current.revoked_at is not None
            or current_expiration <= now
            or current.user_id != user_id
        ):
            raise api_error(
                status.HTTP_401_UNAUTHORIZED,
                "expired_refresh_session",
                "La sesión expiró. Inicia sesión nuevamente.",
            )
        user = self.db.get(User, user_id)
        if not user or not user.is_active:
            raise api_error(
                status.HTTP_401_UNAUTHORIZED,
                "inactive_user",
                "La cuenta no está disponible.",
            )
        access_token, _, _ = create_token(user.id, "access", self.settings)
        new_refresh, new_id, expires_at = create_token(user.id, "refresh", self.settings)
        current.revoked_at = now
        current.replaced_by = new_id
        self.db.add(
            RefreshSession(id=new_id, user_id=user.id, expires_at=expires_at)
        )
        self.db.commit()
        return user, access_token, new_refresh

    def revoke_session(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        try:
            payload = decode_token(refresh_token, "refresh", self.settings)
            session_id = UUID(payload["jti"])
        except (jwt.InvalidTokenError, KeyError, ValueError):
            return
        current = self.db.get(RefreshSession, session_id)
        if current and current.revoked_at is None:
            current.revoked_at = datetime.now(UTC)
            self.db.commit()
