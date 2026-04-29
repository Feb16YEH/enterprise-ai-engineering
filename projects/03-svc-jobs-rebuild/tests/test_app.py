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


def test_create_job_runs_to_done(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        headers={"Authorization": "Bearer token-alice"},
        json={
            "task_type": "report_export",
            "payload": {"report_name": "daily_sales"},
            "simulate_seconds": 0,
            "should_fail": False,
        },
    )

    assert response.status_code == 202
    accepted = response.json()
    assert accepted["status"] == "PENDING"

    job_id = accepted["job_id"]
    detail_response = client.get(
        f"/jobs/{job_id}",
        headers={"Authorization": "Bearer token-alice"},
    )

    assert detail_response.status_code == 200
    job = detail_response.json()
    assert job["status"] == "DONE"
    assert job["result_summary"] == "report_export completed for daily_sales"
    assert job["error_message"] is None
    assert job["started_at"] is not None
    assert job["finished_at"] is not None
    assert job["duration_ms"] is not None


def test_create_job_records_failure(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        headers={"Authorization": "Bearer token-alice"},
        json={
            "task_type": "data_extract",
            "payload": {"source": "warehouse.fact_sales"},
            "simulate_seconds": 0,
            "should_fail": True,
        },
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    detail_response = client.get(
        f"/jobs/{job_id}",
        headers={"Authorization": "Bearer token-alice"},
    )

    assert detail_response.status_code == 200
    job = detail_response.json()
    assert job["status"] == "FAILED"
    assert job["result_summary"] is None
    assert job["error_message"] == "simulated job failure"
    assert job["finished_at"] is not None
    assert job["duration_ms"] is not None


def test_get_job_not_found(client: TestClient) -> None:
    response = client.get(
        "/jobs/999",
        headers={"Authorization": "Bearer token-alice"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error_code"] == "JOB_NOT_FOUND"
    assert body["trace_id"] == response.headers["x-request-id"]


def test_get_job_forbidden_for_other_user(client: TestClient) -> None:
    # Create a job with alice
    create_response = client.post(
        "/jobs",
        headers={"Authorization": "Bearer token-alice"},
        json={
            "task_type": "report_export",
            "payload": {"report_name": "daily_sales"},
            "simulate_seconds": 0,
            "should_fail": False,
        },
    )
    job_id = create_response.json()["job_id"]

    response = client.get(
        f"/jobs/{job_id}",
        headers={"Authorization": "Bearer token-bob"},
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "JOB_FORBIDDEN"


def test_list_jobs_returns_current_user_jobs(client: TestClient) -> None:
    client.post(
        "/jobs",
        headers={"Authorization": "Bearer token-alice"},
        json={
            "task_type": "report_export",
            "payload": {"report_name": "alice_report"},
            "simulate_seconds": 0,
        },
    )

    client.post(
        "/jobs",
        headers={"Authorization": "Bearer token-bob"},
        json={
            "task_type": "load_table",
            "payload": {"report_name": "bob_table"},
            "simulate_seconds": 0,
        },
    )

    response = client.get(
        "/jobs",
        headers={"Authorization": "Bearer token-alice"},
    )

    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 1
    assert jobs[0]["submitted_by"] == "alice"
    assert jobs[0]["payload"]["report_name"] == "alice_report"