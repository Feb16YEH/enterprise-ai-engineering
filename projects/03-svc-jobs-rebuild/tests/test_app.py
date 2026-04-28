from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import get_session
from app.main import create_app
from app.services.jobs import _run_job_with_session, get_job_runner


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient]:
    database_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Generator[Session]:
        with Session(engine) as session:
            yield session

    def test_job_runner(job_id: int) -> None:
        with Session(engine) as session:
            _run_job_with_session(job_id=job_id, session=session)

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_job_runner] = lambda: test_job_runner

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-request-id" in response.headers


def test_version(client: TestClient) -> None:
    response = client.get("/version")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "03-svc-jobs-rebuild"
    assert body["version"] == "0.1.0"


def test_token_sucess(client: TestClient) -> None:
    response = client.post(
        "/token",
        data={"username": "alice", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "token-alice",
        "token_type": "bearer",
    }


def test_token_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/token",
        data={"username": "alice", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"
