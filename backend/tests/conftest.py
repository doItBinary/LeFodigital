from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.models import User, UserRole
from app.db.session import get_db
from app.main import app


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="dev",
        database_url="sqlite+pysqlite:///:memory:",
        jwt_secret_key="test-secret-key-with-more-than-thirty-two-characters",
        teacher_invitation_code="DOCENTE-TEST",
        evidence_storage_path=tmp_path / "evidence",
        openai_api_key="",
        chat_rate_limit_per_minute=100,
    )


@pytest.fixture
def session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session


@pytest.fixture
def users(db: Session) -> dict[str, User]:
    teacher = User(
        name="Profesor Demo",
        email="prof@demo.com",
        password_hash=hash_password("prof123"),
        role=UserRole.TEACHER,
    )
    student = User(
        name="Estudiante Demo",
        email="est@demo.com",
        password_hash=hash_password("est123"),
        role=UserRole.STUDENT,
    )
    db.add_all([teacher, student])
    db.commit()
    db.refresh(teacher)
    db.refresh(student)
    return {"teacher": teacher, "student": student}


@pytest.fixture
def client(
    session_factory: sessionmaker[Session],
    settings: Settings,
    users: dict[str, User],
) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


@pytest.fixture
def teacher_headers(client: TestClient) -> dict[str, str]:
    return login(client, "prof@demo.com", "prof123")


@pytest.fixture
def student_headers(client: TestClient) -> dict[str, str]:
    return login(client, "est@demo.com", "est123")
