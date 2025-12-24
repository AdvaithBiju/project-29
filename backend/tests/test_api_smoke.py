import os
from fastapi.testclient import TestClient

# Use SQLite for isolated tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.main import app  # noqa: E402
from app.db import Base, engine  # noqa: E402

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_auth_and_profile_flow():
    register_resp = client.post("/auth/register", json={"email": "test@example.com", "password": "secret"})
    assert register_resp.status_code == 200
    login_resp = client.post("/auth/login", json={"email": "test@example.com", "password": "secret"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "name": "Alex",
        "sex": "male",
        "dob": "1990-01-01",
        "height_cm": 180,
        "weight_kg": 80,
        "location_country": "USA",
        "conditions": ["hypertension"],
        "meds": ["lisinopril"],
    }
    profile_resp = client.post("/profiles", json=profile_payload, headers=headers)
    assert profile_resp.status_code == 200
    profile_id = profile_resp.json()["id"]

    list_resp = client.get("/profiles", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Upload sample report using fixture text as file
    sample_text_path = "backend/tests/fixtures/pdf_text.txt"
    with open(sample_text_path, "rb") as f:
        files = {"file": ("report.txt", f, "application/pdf")}
        upload_resp = client.post(
            f"/profiles/{profile_id}/reports",
            files=files,
            headers=headers,
        )
    assert upload_resp.status_code == 200
    report_id = upload_resp.json()["id"]

    insights_resp = client.get(f"/profiles/{profile_id}/reports/{report_id}/insights", headers=headers)
    assert insights_resp.status_code == 200
    data = insights_resp.json()
    assert data["report_id"] == report_id
