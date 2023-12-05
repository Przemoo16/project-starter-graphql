from uuid import UUID

import pytest

from tests.integration.conftest import AsyncClient, AsyncSession
from tests.integration.helpers.user import (
    create_confirmed_user,
    create_email_confirmation_token,
    create_user,
)


@pytest.mark.anyio()
async def test_confirm_email(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_user(db)
    token = create_email_confirmation_token(auth_private_key, user.id, user.email)
    query = """
      mutation ConfirmEmail($token: String!) {
        confirmEmail(token: $token) {
          ... on ConfirmEmailSuccess {
            message
          }
        }
      }
    """
    variables = {"token": token}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["confirmEmail"]
    assert "message" in data


@pytest.mark.anyio()
async def test_confirm_email_invalid_token(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation ConfirmEmail($token: String!) {
        confirmEmail(token: $token) {
          ... on ConfirmEmailFailure {
            problems {
              ... on InvalidEmailConfirmationTokenProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {"token": "invalid-token"}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problem = response.json()["data"]["confirmEmail"]["problems"][0]
    assert "message" in problem


@pytest.mark.anyio()
async def test_confirm_email_user_not_found(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    token = create_email_confirmation_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), "test@email.com"
    )
    query = """
      mutation ConfirmEmail($token: String!) {
        confirmEmail(token: $token) {
          ... on ConfirmEmailFailure {
            problems {
              ... on InvalidEmailConfirmationTokenProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {"token": token}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problem = response.json()["data"]["confirmEmail"]["problems"][0]
    assert "message" in problem


@pytest.mark.anyio()
async def test_confirm_email_user_email_already_confirmed(
    db: AsyncSession, auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    user = await create_confirmed_user(db)
    token = create_email_confirmation_token(auth_private_key, user.id, user.email)
    query = """
      mutation ConfirmEmail($token: String!) {
        confirmEmail(token: $token) {
          ... on ConfirmEmailFailure {
            problems {
              ... on UserEmailAlreadyConfirmedProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {"token": token}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problem = response.json()["data"]["confirmEmail"]["problems"][0]
    assert "message" in problem
