from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.modules.auth.schemas import (
    AuthSession,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.schemas import UserProfile


router = APIRouter(prefix="/auth", tags=["Autenticación"])


def set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path=f"{settings.api_prefix}/auth",
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RegisterResponse:
    user = AuthService(db, settings).register(data)
    return RegisterResponse(message="Cuenta creada. Ya puedes iniciar sesión.", user=user)


@router.post("/login", response_model=AuthSession)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AuthSession:
    service = AuthService(db, settings)
    user = service.authenticate(data)
    access_token, refresh_token = service.create_session(user)
    set_refresh_cookie(response, refresh_token, settings)
    return AuthSession(
        access_token=access_token,
        expires_in=settings.access_token_minutes * 60,
        user=UserProfile.model_validate(user),
    )


@router.post("/refresh", response_model=AuthSession)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="lefodigital_refresh"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AuthSession:
    service = AuthService(db, settings)
    user, access_token, new_refresh = service.rotate_session(refresh_token or "")
    set_refresh_cookie(response, new_refresh, settings)
    return AuthSession(
        access_token=access_token,
        expires_in=settings.access_token_minutes * 60,
        user=UserProfile.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="lefodigital_refresh"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    AuthService(db, settings).revoke_session(refresh_token)
    response.delete_cookie(
        settings.refresh_cookie_name,
        path=f"{settings.api_prefix}/auth",
        secure=settings.is_production,
        httponly=True,
        samesite="lax",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
