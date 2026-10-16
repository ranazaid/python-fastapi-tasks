"""End-to-end API tests using an isolated in-memory SQLite database.

Run with:  pytest -q
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # One shared in-memory connection for the whole test (StaticPool).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_fetch(client):
    resp = client.post("/tasks", json={"title": "Write README"})
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Write README"
    assert created["status"] == "todo"

    got = client.get(f"/tasks/{created['id']}")
    assert got.status_code == 200
    assert got.json()["id"] == created["id"]


def test_partial_update(client):
    task_id = client.post("/tasks", json={"title": "Ship it"}).json()["id"]
    resp = client.patch(f"/tasks/{task_id}", json={"status": "done"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "done"
    assert body["title"] == "Ship it"  # untouched


def test_filter_by_status(client):
    client.post("/tasks", json={"title": "a", "status": "todo"})
    client.post("/tasks", json={"title": "b", "status": "done"})
    done = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in done] == ["b"]


def test_delete_then_404(client):
    task_id = client.post("/tasks", json={"title": "temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_validation_rejects_empty_title(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
