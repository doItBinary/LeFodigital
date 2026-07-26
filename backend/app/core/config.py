from functools import lru_cache
import os
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LeFodigital API"
    app_env: Literal["dev", "prod"] = "dev"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/prj_grado_dev"
    jwt_secret_key: str = "change-this-development-secret-with-at-least-32-characters"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "lefodigital"
    jwt_audience: str = "lefodigital-web"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    teacher_invitation_code: str = "change-me"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    evidence_storage_path: Path = Path("./data/evidence")
    max_upload_bytes: int = 1_048_576
    chat_rate_limit_per_minute: int = 10
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:4200"]
    )
    seed_demo_data: bool = True
    log_level: str = "info"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "prod"

    @property
    def refresh_cookie_name(self) -> str:
        return "lefodigital_refresh"


@lru_cache
def get_settings() -> Settings:
    env_file = ".env" if os.getenv("APP_ENV", "dev").lower() == "dev" else None
    return Settings(_env_file=env_file)
