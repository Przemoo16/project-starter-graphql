import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.main import get_local_app


@pytest.mark.parametrize("url", ["/docs", "/redoc"])
def test_openapi_documentation_is_disabled(url: str, engine: AsyncEngine) -> None:
    app = get_local_app(engine)

    with TestClient(app) as client:
        response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "debug,status_code",
    [(True, status.HTTP_200_OK), (False, status.HTTP_404_NOT_FOUND)],
)
def test_enable_disable_graphiql(
    debug: bool, status_code: int, engine: AsyncEngine
) -> None:
    app = get_local_app(engine, debug)

    with TestClient(app) as client:
        response = client.get("/graphql")

    assert response.status_code == status_code
