import pytest
from fastapi import status
from httpx import AsyncClient

from backend.main import get_local_app
from tests.integration.conftest import AsyncEngine


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("debug", "status_code"),
    [(True, status.HTTP_200_OK), (False, status.HTTP_404_NOT_FOUND)],
)
async def test_enable_disable_graphiql(
    debug: bool, status_code: int, db_engine: AsyncEngine, graphql_url: str
) -> None:
    app = get_local_app(db_engine, debug)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(graphql_url)

    assert response.status_code == status_code


@pytest.mark.anyio()
@pytest.mark.parametrize(("debug", "error"), [(True, False), (False, True)])
async def test_enable_disable_schema_introspection(
    debug: bool, error: bool, db_engine: AsyncEngine, graphql_url: str
) -> None:
    app = get_local_app(db_engine, debug)
    payload = {
        "query": """
          query {
            __schema {
              types {
                name
              }
            }
          }
        """
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(graphql_url, json=payload)

    assert bool(response.json().get("errors")) == error
