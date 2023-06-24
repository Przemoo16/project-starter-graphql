import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import create_user


@pytest.mark.anyio()
async def test_create_user(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              createUser(user: {email: "test@email.com", password: "plain_password"}) {
                __typename
                ... on User {
                  id
                  email
                }
                ... on UserAlreadyExists {
                  message
                  email
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]
    assert data["__typename"] == "User"
    assert "id" in data
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_already_exists(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, email="test@email.com")
    payload = {
        "query": """
            mutation {
              createUser(user: {email: "test@email.com", password: "plain_password"}) {
                __typename
                ... on User {
                  id
                  email
                }
                ... on UserAlreadyExists {
                  message
                  email
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]
    assert data["__typename"] == "UserAlreadyExists"
    assert "message" in data
    assert data["email"] == "test@email.com"
