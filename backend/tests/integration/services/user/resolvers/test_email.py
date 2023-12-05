from uuid import UUID

import pytest

from tests.integration.conftest import AsyncClient, AsyncSession
from tests.integration.helpers.user import (
    create_access_token,
    create_confirmed_user,
    create_email_confirmation_token,
    create_user,
)


@pytest.mark.anyio()
async def test_confirm_email_returns_success_message(
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
async def test_confirm_email_returns_problem_if_token_is_invalid(
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
async def test_confirm_email_returns_problem_if_token_has_invalid_type(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    token = create_access_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
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
async def test_confirm_email_returns_problem_if_user_with_encoded_id_is_not_found(
    db: AsyncSession, auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    user = await create_user(db)
    token = create_email_confirmation_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), user.email
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
async def test_confirm_email_returns_problem_if_user_with_encoded_email_is_not_found(
    db: AsyncSession, auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    user = await create_user(db)
    token = create_email_confirmation_token(
        auth_private_key, user.id, "invalid@email.com"
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
async def test_confirm_email_returns_problem_if_user_email_is_already_confirmed(
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
