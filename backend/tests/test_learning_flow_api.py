from io import BytesIO

from fastapi.testclient import TestClient

from app.modules.evidences.service import sanitize_original_name


def create_and_publish_activity(
    client: TestClient,
    teacher_headers: dict[str, str],
) -> str:
    course = client.post(
        "/api/v1/courses",
        headers=teacher_headers,
        json={"name": "Competencias digitales", "description": "Curso de prueba"},
    )
    assert course.status_code == 201
    activity = client.post(
        "/api/v1/activities",
        headers=teacher_headers,
        json={
            "title": "Identificar riesgos digitales",
            "description": "Analiza una situación cotidiana.",
            "points": 50,
            "courseId": course.json()["id"],
        },
    )
    assert activity.status_code == 201
    assert activity.json()["status"] == "draft"
    return activity.json()["id"]


def test_complete_learning_flow_and_consistent_delete(
    client: TestClient,
    teacher_headers: dict[str, str],
    student_headers: dict[str, str],
) -> None:
    activity_id = create_and_publish_activity(client, teacher_headers)

    student_before = client.get("/api/v1/activities", headers=student_headers)
    assert student_before.json() == []

    published = client.post(
        f"/api/v1/activities/{activity_id}/publish",
        headers=teacher_headers,
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    evidence = client.post(
        f"/api/v1/activities/{activity_id}/evidence",
        headers=student_headers,
        files={"file": ("evidencia.pdf", BytesIO(b"%PDF-1.4 test"), "application/pdf")},
    )
    assert evidence.status_code == 200
    evidence_id = evidence.json()["id"]

    duplicate_evidence = client.post(
        f"/api/v1/activities/{activity_id}/evidence",
        headers=student_headers,
        files={"file": ("otra.pdf", BytesIO(b"%PDF-1.4 duplicate"), "application/pdf")},
    )
    assert duplicate_evidence.status_code == 409

    completion = client.post(
        f"/api/v1/activities/{activity_id}/complete",
        headers=student_headers,
    )
    assert completion.status_code == 200
    assert completion.json()["activity"]["completed"]
    second_completion = client.post(
        f"/api/v1/activities/{activity_id}/complete",
        headers=student_headers,
    )
    assert second_completion.status_code == 200

    progress = client.get("/api/v1/gamification/me", headers=student_headers).json()
    assert progress["points"] == 50
    assert progress["completedActivities"] == 1
    assert {item["key"] for item in progress["medals"]} == {
        "first_task",
        "points_50",
        "first_evidence",
    }

    teacher_evidences = client.get(
        f"/api/v1/activities/{activity_id}/evidences",
        headers=teacher_headers,
    )
    assert teacher_evidences.status_code == 200
    assert teacher_evidences.json()[0]["studentName"] == "Estudiante Demo"

    download = client.get(
        f"/api/v1/evidences/{evidence_id}/download",
        headers=student_headers,
    )
    assert download.status_code == 200
    assert download.content.startswith(b"%PDF")

    removed = client.delete(
        f"/api/v1/activities/{activity_id}",
        headers=teacher_headers,
    )
    assert removed.status_code == 204
    after_delete = client.get("/api/v1/gamification/me", headers=student_headers).json()
    assert after_delete["points"] == 0
    assert after_delete["medals"] == []


def test_role_permissions_and_file_validation(
    client: TestClient,
    teacher_headers: dict[str, str],
    student_headers: dict[str, str],
) -> None:
    forbidden_course = client.post(
        "/api/v1/courses",
        headers=student_headers,
        json={"name": "No permitido", "description": ""},
    )
    assert forbidden_course.status_code == 403
    activity_id = create_and_publish_activity(client, teacher_headers)
    client.post(f"/api/v1/activities/{activity_id}/publish", headers=teacher_headers)
    invalid = client.post(
        f"/api/v1/activities/{activity_id}/evidence",
        headers=student_headers,
        files={"file": ("malware.exe", BytesIO(b"MZ"), "application/octet-stream")},
    )
    assert invalid.status_code == 415
    mismatched = client.post(
        f"/api/v1/activities/{activity_id}/evidence",
        headers=student_headers,
        files={"file": ("archivo.pdf", BytesIO(b"not-an-image"), "image/png")},
    )
    assert mismatched.status_code == 415


def test_blog_contact_and_reports(
    client: TestClient,
    teacher_headers: dict[str, str],
    student_headers: dict[str, str],
) -> None:
    post = client.post(
        "/api/v1/posts",
        headers=student_headers,
        json={"title": "Mi aprendizaje", "content": "Aprendí a proteger mis datos."},
    )
    assert post.status_code == 201
    comment = client.post(
        f"/api/v1/posts/{post.json()['id']}/comments",
        headers=teacher_headers,
        json={"content": "Excelente reflexión."},
    )
    assert comment.status_code == 201
    assert len(comment.json()["comments"]) == 1
    assert len(client.get("/api/v1/posts", headers=student_headers).json()) == 1

    contact = client.post(
        "/api/v1/contact-messages",
        headers=student_headers,
        json={"subject": "Consulta", "message": "Necesito más información."},
    )
    assert contact.status_code == 201

    student_report = client.get(
        "/api/v1/reports/student/me", headers=student_headers
    )
    assert student_report.status_code == 200
    teacher_report = client.get("/api/v1/reports/teacher", headers=teacher_headers)
    assert teacher_report.status_code == 200
    assert teacher_report.json()["totalStudents"] == 1
    assert client.get("/api/v1/reports/teacher", headers=student_headers).status_code == 403


def test_health_and_unconfigured_chat(client: TestClient) -> None:
    assert client.get("/api/v1/health/live").json() == {"status": "ok"}
    response = client.post(
        "/api/v1/chat/messages",
        json={"messages": [{"role": "user", "content": "Hola"}]},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "chat_not_configured"


def test_evidence_filename_is_sanitized() -> None:
    assert sanitize_original_name(r"..\private\report.pdf") == "report.pdf"
    assert sanitize_original_name('../../private/"report".pdf') == "report.pdf"
