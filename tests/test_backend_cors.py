from fastapi.testclient import TestClient

from backend.app import app


def test_unconfigured_origin_gets_no_cors_access():
    response = TestClient(app).get(
        "/health",
        headers={"Origin": "https://not-configured.example.invalid"},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
