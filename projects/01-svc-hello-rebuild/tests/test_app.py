from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "01-svc-hello-rebuild"
    assert body["version"] == "0.1.0"


def test_echo():
    response = client.post("/echo", json={"message": "Hello AI"})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello AI"
    assert body["length"] == 8
    assert "request_id" in body


def test_echo_business_error():
    response = client.post("/echo", json={"message": "error"})

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "ECHO_BAD_MESSAGE"
    assert body["message"] == "message cannot be error"
    assert "trace_id" in body


def test_echo_validation_error():
    response = client.post("/echo", json={"message": ""})

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert "message" in body
    assert "trace_id" in body

