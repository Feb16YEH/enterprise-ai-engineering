from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


TEST_DATABASE_URL = "sqlite:///./test_svc_catalog.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def override_get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


def get_access_token() -> str:
    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"},
    )
    return response.json()["access_token"]

def test_list_reports_without_token_returns_401() -> None:
    response = client.get("/reports")
    assert response.status_code == 401


def test_list_reports_with_wrong_token_returns_401() -> None:
    response = client.get(
        "/reports",
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_create_and_get_report_with_valid_token() -> None:
    token = get_access_token()
    headers ={"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/reports",
        headers=headers,
        json={
            "name": "Monthly Revenue Report",
            "owner": "finance",
            "sql_template": "select * from revenue",
            "description": "Monthly revenue report for finance team",
        },
    )

    assert create_response.status_code == 201

    created_report = create_response.json()
    report_id = created_report["id"]

    get_response = client.get(f"/reports/{report_id}", headers=headers)

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Monthly Revenue Report"


def test_get_report_not_found_returns_404() -> None:
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/reports/99999", headers=headers)

    assert response.status_code == 404