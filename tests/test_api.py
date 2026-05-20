import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.name}"

from backend.database import init_db  # noqa: E402
from backend.main import app  # noqa: E402

init_db()
client = TestClient(app)


@pytest.fixture
def auth_headers():
    email = f"pytest-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "testpass1", "name": "Py Test"},
    )
    r = client.post("/api/auth/login", json={"email": email, "password": "testpass1"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_me(auth_headers):
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert "@example.com" in r.json()["email"]


def test_course_crud(auth_headers):
    r = client.post(
        "/api/courses",
        headers=auth_headers,
        json={"name": "Biology", "color": "#22c55e", "syllabus_url": "https://example.com/syllabus"},
    )
    assert r.status_code == 201
    course_id = r.json()["id"]

    r = client.get(f"/api/courses/{course_id}/detail", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["syllabus_url"] == "https://example.com/syllabus"

    r = client.patch(
        f"/api/courses/{course_id}",
        headers=auth_headers,
        json={"teacher": "Dr. Lee"},
    )
    assert r.status_code == 200
    assert r.json()["teacher"] == "Dr. Lee"


def test_assignment_with_category(auth_headers):
    c = client.post(
        "/api/courses",
        headers=auth_headers,
        json={"name": "History", "color": "#a855f7"},
    ).json()
    r = client.post(
        "/api/assignments",
        headers=auth_headers,
        json={
            "course_id": c["id"],
            "title": "Midterm",
            "category": "exam",
            "due_date": "2030-06-01",
        },
    )
    assert r.status_code == 201
    assert r.json()["category"] == "exam"

    r = client.get(f"/api/assignments?course_id={c['id']}", headers=auth_headers)
    assert len(r.json()) >= 1


def test_study_session_and_csv_export(auth_headers):
    c = client.post(
        "/api/courses",
        headers=auth_headers,
        json={"name": "Math", "color": "#3b82f6"},
    ).json()
    r = client.post(
        "/api/sessions",
        headers=auth_headers,
        json={"course_id": c["id"], "minutes": 45, "date": "2026-05-01"},
    )
    assert r.status_code == 201

    r = client.get("/api/sessions/export.csv", headers=auth_headers)
    assert r.status_code == 200
    assert "course" in r.text
    assert "Math" in r.text


def test_dashboard_completion_and_goals(auth_headers):
    c = client.post(
        "/api/courses",
        headers=auth_headers,
        json={"name": "Chem", "color": "#ef4444"},
    ).json()
    client.post(
        "/api/assignments",
        headers=auth_headers,
        json={"course_id": c["id"], "title": "Lab 1", "status": "done"},
    )
    client.post(
        "/api/assignments",
        headers=auth_headers,
        json={"course_id": c["id"], "title": "Lab 2", "status": "todo"},
    )
    client.post(
        "/api/goals",
        headers=auth_headers,
        json={"course_id": c["id"], "weekly_minutes": 120},
    )
    r = client.get("/api/dashboard", headers=auth_headers)
    data = r.json()
    assert data["assignments_total"] >= 2
    assert data["completion_rate"] >= 0
    assert len(data["study_goals"]) >= 1


def test_calendar(auth_headers):
    c = client.post(
        "/api/courses",
        headers=auth_headers,
        json={"name": "English", "color": "#f59e0b"},
    ).json()
    client.post(
        "/api/assignments",
        headers=auth_headers,
        json={"course_id": c["id"], "title": "Essay", "due_date": "2026-05-15"},
    )
    r = client.get("/api/calendar?year=2026&month=5", headers=auth_headers)
    assert r.status_code == 200
    assert "2026-05-15" in r.json()["days"]


def test_profile_update(auth_headers):
    r = client.patch(
        "/api/profile",
        headers=auth_headers,
        json={"name": "Updated Name", "email_reminders_enabled": False},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Name"
    assert r.json()["email_reminders_enabled"] is False
