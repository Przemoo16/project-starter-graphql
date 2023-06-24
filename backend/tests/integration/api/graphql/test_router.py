import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.main import get_local_app


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("debug", "status_code"),
    [(True, status.HTTP_200_OK), (False, status.HTTP_404_NOT_FOUND)],
)
async def test_enable_disable_graphiql(
    debug: bool, status_code: int, engine: AsyncEngine
) -> None:
    app = get_local_app(engine, debug)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/graphql")

    assert response.status_code == status_code


@pytest.mark.anyio()
@pytest.mark.parametrize(("debug", "error"), [(True, False), (False, True)])
async def test_enable_disable_schema_introspection(
    debug: bool, error: bool, engine: AsyncEngine
) -> None:
    app = get_local_app(engine, debug)
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
        response = await client.post("/graphql", json=payload)

    assert bool(response.json().get("errors")) == error