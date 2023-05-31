from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_main() -> None:
    response = client.get("/")

    assert response.status_code == 200