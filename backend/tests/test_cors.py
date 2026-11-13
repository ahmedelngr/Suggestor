from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def preflight(origin):
    return client.options(
        "/feed",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )


def test_allowed_origin_gets_cors_headers():
    response = preflight("http://localhost:8081")
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8081"


def test_other_origin_is_refused():
    response = preflight("https://other.example")
    assert "access-control-allow-origin" not in response.headers
