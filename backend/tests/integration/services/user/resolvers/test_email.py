from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_confirmed_user,
    create_email_confirmation_token,
    create_user,
)


@pytest.mark.anyio()
async def test_confirm_email(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_user(
        session, id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
    )
    token = create_email_confirmation_token(auth_private_key, user.id, user.email)
    payload = {
        "query": f"""
            mutation {{
              confirmEmail(token: "{token}") {{
                ... on ConfirmEmailSuccess {{
                   id
                   email
                }}
              }}
            }}
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["confirmEmail"]
    assert data["id"] == "6d9c79d6-9641-4746-92d9-2cc9ebdca941"
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_confirm_email_invalid_token(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              confirmEmail(token: "invalid-token") {
                ... on ConfirmEmailFailure {
                  problems {
                    ... on InvalidEmailConfirmationToken {
                      message
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["confirmEmail"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_confirm_email_user_already_confirmed(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(
        session, id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
    )
    token = create_email_confirmation_token(auth_private_key, user.id, user.email)
    payload = {
        "query": f"""
            mutation {{
              confirmEmail(token: "{token}") {{
                ... on ConfirmEmailFailure {{
                  problems {{
                    ... on UserAlreadyConfirmed {{
                      message
                    }}
                  }}
                }}
              }}
            }}
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["confirmEmail"]["problems"][0]
    assert "message" in data
