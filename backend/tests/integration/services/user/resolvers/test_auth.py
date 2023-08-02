from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_confirmed_user,
    create_refresh_token,
    create_user,
    hash_password,
)


@pytest.mark.anyio()
async def test_login(session: AsyncSession, async_client: AsyncClient) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    query = """
      mutation Login($input: LoginInput!) {
        login(input: $input) {
          ... on LoginSuccess {
            accessToken
            refreshToken
            tokenType
          }
        }
      }
    """
    variables = {
        "input": {
            "username": "test@email.com",
            "password": "plain_password",
        },
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["login"]
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_login_user_not_found(async_client: AsyncClient) -> None:
    query = """
      mutation Login($input: LoginInput!) {
        login(input: $input) {
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
    variables = {
        "input": {
            "username": "test@email.com",
            "password": "plain_password",
        },
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_login_invalid_password(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    query = """
      mutation Login($input: LoginInput!) {
        login(input: $input) {
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
    variables = {
        "input": {
            "username": "test@email.com",
            "password": "invalid_password",
        },
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_login_user_not_confirmed(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    query = """
      mutation Login($input: LoginInput!) {
        login(input: $input) {
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
    variables = {
        "input": {
            "username": "test@email.com",
            "password": "plain_password",
        },
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_refresh_token(auth_private_key: str, async_client: AsyncClient) -> None:
    token = create_refresh_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    )
    query = """
      mutation RefreshToken($token: String!) {
        refreshToken(token: $token) {
          accessToken
          tokenType
        }
      }
    """
    variables = {"token": token}

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["refreshToken"]
    assert "accessToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_refresh_token_invalid_token(async_client: AsyncClient) -> None:
    query = """
      mutation RefreshToken($token: String!) {
        refreshToken(token: $token) {
          accessToken
        }
      }
    """
    variables = {"token": "invalid-token"}

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    errors = response.json()["errors"]
    assert errors[0]["message"] == "Invalid token"
