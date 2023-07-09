from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_confirmed_user,
    create_reset_password_token,
    create_user,
)


@pytest.mark.anyio()
async def test_recover_password(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_confirmed_user(session, email="test@email.com")
    payload = {
        "query": """
            mutation {
              recoverPassword(email: "test@email.com") {
                message
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["recoverPassword"]
    assert "message" in data


@pytest.mark.anyio()
async def test_recover_password_user_not_found(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              recoverPassword(email: "test@email.com") {
                message
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["recoverPassword"]
    assert data


@pytest.mark.anyio()
async def test_recover_password_user_not_confirmed(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(session, email="test@email.com")
    payload = {
        "query": """
            mutation {
              recoverPassword(email: "test@email.com") {
                message
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["recoverPassword"]
    assert data


@pytest.mark.anyio()
async def test_reset_password(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(session)
    token = create_reset_password_token(auth_private_key, user.id, user.hashed_password)
    payload = {
        "query": f"""
            mutation {{
              resetPassword(input: {{token: "{token}", password: "new_password"}}) {{
                ... on ResetPasswordSuccess {{
                  message
                }}
              }}
            }}
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_invalid_input(
    auth_private_key: str, async_client: AsyncClient
) -> None:
    token = create_reset_password_token(
        auth_private_key,
        UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        "hashed_password",
    )
    payload = {
        "query": f"""
            mutation {{
              resetPassword(input: {{token: "{token}", password: "p"}}) {{
                ... on ResetPasswordFailure {{
                  problems {{
                    __typename
                  }}
                }}
              }}
            }}
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert data["__typename"] == "InvalidInput"


@pytest.mark.anyio()
async def test_reset_password_invalid_token(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              resetPassword(input: {token: "invalid-token", password: "new_password"}) {
                ... on ResetPasswordFailure {
                  problems {
                    ... on InvalidResetPasswordToken {
                      message
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_user_not_confirmed(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_user(session)
    token = create_reset_password_token(auth_private_key, user.id, user.hashed_password)
    payload = {
        "query": f"""
            mutation {{
              resetPassword(input: {{token: "{token}", password: "new_password"}}) {{
                ... on ResetPasswordFailure {{
                  problems {{
                    ... on InvalidResetPasswordToken {{
                      message
                    }}
                  }}
                }}
              }}
            }}
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_cannot_use_same_token_twice(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(session)
    token = create_reset_password_token(auth_private_key, user.id, user.hashed_password)
    payload = {
        "query": f"""
            mutation {{
              resetPassword(input: {{token: "{token}", password: "new_password"}}) {{
                ... on ResetPasswordFailure {{
                  problems {{
                    __typename
                  }}
                }}
              }}
            }}
        """
    }

    await async_client.post("/graphql", json=payload)
    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert data["__typename"] == "InvalidResetPasswordToken"
