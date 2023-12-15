from uuid import UUID

import pytest

from tests.integration.conftest import AsyncClient, AsyncSession
from tests.integration.helpers.user import (
    create_access_token,
    create_confirmed_user,
    create_refresh_token,
    create_user,
    hash_password,
)


@pytest.mark.anyio()
async def test_login_returns_tokens(
    db: AsyncSession, client: AsyncClient, graphql_url: str
) -> None:
    await create_confirmed_user(
        db, email="test@email.com", hashed_password=hash_password("plain_password")
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

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["login"]
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_login_returns_problem_if_user_is_not_found(
    client: AsyncClient, graphql_url: str
) -> None:
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

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problems = response.json()["data"]["login"]["problems"]
    assert len(problems) == 1
    assert "message" in problems[0]


@pytest.mark.anyio()
async def test_login_returns_problem_if_password_is_invalid(
    db: AsyncSession, client: AsyncClient, graphql_url: str
) -> None:
    await create_confirmed_user(
        db, email="test@email.com", hashed_password=hash_password("plain_password")
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

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problems = response.json()["data"]["login"]["problems"]
    assert len(problems) == 1
    assert "message" in problems[0]


@pytest.mark.anyio()
async def test_login_returns_problem_if_user_email_is_not_confirmed(
    db: AsyncSession, client: AsyncClient, graphql_url: str
) -> None:
    await create_user(
        db, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    query = """
      mutation Login($input: LoginInput!) {
        login(input: $input) {
          ... on LoginFailure {
            problems {
              ... on UserEmailNotConfirmedProblem {
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

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problems = response.json()["data"]["login"]["problems"]
    assert len(problems) == 1
    assert "message" in problems[0]


@pytest.mark.anyio()
async def test_refresh_token_returns_access_token(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
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

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["refreshToken"]
    assert "accessToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_refresh_token_returns_error_if_token_is_invalid(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation RefreshToken($token: String!) {
        refreshToken(token: $token) {
          accessToken
        }
      }
    """
    variables = {"token": "invalid-token"}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    errors = response.json()["errors"]
    assert len(errors) == 1
    assert errors[0]["message"] == "Invalid token"


@pytest.mark.anyio()
async def test_refresh_token_returns_error_if_token_has_invalid_type(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    token = create_access_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    )
    query = """
      mutation RefreshToken($token: String!) {
        refreshToken(token: $token) {
          accessToken
        }
      }
    """
    variables = {"token": token}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    errors = response.json()["errors"]
    assert len(errors) == 1
    assert errors[0]["message"] == "Invalid token"
