import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.main import get_local_app


@pytest.mark.anyio()
@pytest.mark.parametrize("url", ["/docs", "/redoc"])
async def test_openapi_documentation_is_disabled(url: str, engine: AsyncEngine) -> None:
    app = get_local_app(engine)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
