from fastapi.testclient import TestClient


def test_login_refresh_logout_cycle(client: TestClient) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "prof@demo.com", "password": "prof123"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "teacher"
    assert login.json()["expiresIn"] == 900
    assert "lefodigital_refresh" in client.cookies

    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["accessToken"] != login.json()["accessToken"]

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert "lefodigital_refresh" not in client.cookies
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "prof@demo.com", "password": "incorrecta"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_registration_rules(client: TestClient) -> None:
    student = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Nueva Estudiante",
            "email": "new@student.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert student.status_code == 201
    assert student.json()["user"]["role"] == "student"

    invalid_teacher = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Docente Nuevo",
            "email": "teacher@example.com",
            "password": "password123",
            "role": "teacher",
            "teacherInvitationCode": "incorrecto",
        },
    )
    assert invalid_teacher.status_code == 403

    teacher = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Docente Nuevo",
            "email": "teacher@example.com",
            "password": "password123",
            "role": "teacher",
            "teacherInvitationCode": "DOCENTE-TEST",
        },
    )
    assert teacher.status_code == 201
    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicado",
            "email": "TEACHER@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert duplicate.status_code == 409


def test_profile_requires_authentication_and_can_be_updated(
    client: TestClient, student_headers: dict[str, str]
) -> None:
    assert client.get("/api/v1/users/me").status_code == 401
    updated = client.patch(
        "/api/v1/users/me",
        headers=student_headers,
        json={"name": "Estudiante Actualizada", "institution": "I.E. Rural"},
    )
    assert updated.status_code == 200
    assert updated.json()["institution"] == "I.E. Rural"
