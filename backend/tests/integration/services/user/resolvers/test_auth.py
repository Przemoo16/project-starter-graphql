import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_confirmed_user,
    create_user,
    hash_password,
)


@pytest.mark.anyio()
async def test_login(session: AsyncSession, async_client: AsyncClient) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginSuccess {
                  accessToken
                  refreshToken
                  tokenType
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_login_user_not_found(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on InvalidCredentialsProblem {
                      message
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_login_invalid_password(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "invalid_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on InvalidCredentialsProblem {
                      message
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_login_user_not_confirmed(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on UserNotConfirmedProblem {
                      message
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data
