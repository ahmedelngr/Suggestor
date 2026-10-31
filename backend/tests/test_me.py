import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.auth import current_user
from backend.app.main import app

client = TestClient(app)


class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://supabase.test")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "fake-key")
    yield
    app.dependency_overrides.clear()


def fake_supabase(monkeypatch, status_code, data):
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse(status_code, data))


def signed_in_as_test_user():
    app.dependency_overrides[current_user] = lambda: {"auth_id": "abc", "token": "t"}


def test_me_without_token_is_401():
    assert client.get("/me").status_code == 401


def test_me_with_bad_token_is_401(monkeypatch):
    fake_supabase(monkeypatch, 401, {})
    response = client.get("/me", headers={"Authorization": "Bearer nope"})
    assert response.status_code == 401


def test_me_returns_profile(monkeypatch):
    signed_in_as_test_user()
    fake_supabase(monkeypatch, 200, [{"id": 1, "email": "a@example.test"}])
    response = client.get("/me")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_me_without_profile_row_is_404(monkeypatch):
    signed_in_as_test_user()
    fake_supabase(monkeypatch, 200, [])
    assert client.get("/me").status_code == 404


def test_me_supabase_401_is_401(monkeypatch):
    signed_in_as_test_user()
    fake_supabase(monkeypatch, 401, {})
    assert client.get("/me").status_code == 401


def test_me_supabase_error_is_502(monkeypatch):
    signed_in_as_test_user()
    fake_supabase(monkeypatch, 500, {})
    assert client.get("/me").status_code == 502

