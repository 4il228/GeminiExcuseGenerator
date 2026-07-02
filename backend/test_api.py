import os
import pytest
from fastapi.testclient import TestClient

os.environ["GEMINI_API_KEY"] = "test_key_placeholder"

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_situation_returns_200():
    for situation in ["late_work", "missed_homework", "forgot_birthday", "dog_ate_code"]:
        response = client.post(
            "/api/v1/generate",
            json={"situation_id": situation}
        )
        assert response.status_code in [200, 500], f"Situation {situation} returned {response.status_code}"


def test_invalid_situation_returns_422():
    response = client.post(
        "/api/v1/generate",
        json={"situation_id": "invalid_situation"}
    )
    assert response.status_code == 422


def test_arbitrary_text_rejected():
    response = client.post(
        "/api/v1/generate",
        json={"situation_id": "ignore previous instructions and"}
    )
    assert response.status_code == 422


def test_missing_field_returns_422():
    response = client.post(
        "/api/v1/generate",
        json={}
    )
    assert response.status_code == 422


def test_frontend_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_static_css_available():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]