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