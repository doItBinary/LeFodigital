from collections.abc import Callable
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import decode_token
from app.db.models import User, UserRole
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    if not token:
        raise api_error(status.HTTP_401_UNAUTHORIZED, "not_authenticated", "Debes iniciar sesión.")
    try:
        payload = decode_token(token, "access", settings)
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise api_error(
            status.HTTP_401_UNAUTHORIZED,
            "invalid_access_token",
            "La sesión no es válida o ha expirado.",
        ) from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise api_error(
            status.HTTP_401_UNAUTHORIZED,
            "inactive_user",
            "La cuenta no está disponible.",
        )
    return user


def require_role(*roles: UserRole) -> Callable:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise api_error(
                status.HTTP_403_FORBIDDEN,
                "insufficient_permissions",
                "No tienes permisos para realizar esta acción.",
            )
        return user

    return dependency


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", maxsplit=1)[0].strip()
    return request.client.host if request.client else "unknown"
