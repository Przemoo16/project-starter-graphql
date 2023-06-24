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
                ... on CreateUserSuccess {
                  id
                  email
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]
    assert data["__typename"] == "CreateUserSuccess"
    assert "id" in data
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_invalid_input(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              createUser(user: {email: "test", password: "plain_password"}) {
                __typename
                ... on CreateUserFailure {
                  problems {
                    __typename
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]["problems"][0]
    assert data["__typename"] == "InvalidInput"


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
                ... on CreateUserFailure {
                  problems {
                    __typename
                    ... on UserAlreadyExists {
                      message
                      email
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]["problems"][0]
    assert data["__typename"] == "UserAlreadyExists"
    assert "message" in data
    assert data["email"] == "test@email.com"
