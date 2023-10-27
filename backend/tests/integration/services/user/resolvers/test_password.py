from uuid import UUID

import pytest

from tests.integration.conftest import AsyncClient, AsyncSession
from tests.integration.helpers.user import (
    create_auth_header,
    create_confirmed_user,
    create_reset_password_token,
    create_user,
    hash_password,
)


@pytest.mark.anyio()
async def test_recover_password(
    db: AsyncSession, client: AsyncClient, graphql_url: str
) -> None:
    await create_user(db, email="test@email.com")
    query = """
      mutation RecoverPassword($email: String!) {
        recoverPassword(email: $email) {
          message
        }
      }
    """
    variables = {"email": "test@email.com"}

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["recoverPassword"]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_user(db)
    token = create_reset_password_token(auth_private_key, user.id, user.hashed_password)
    query = """
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordSuccess {
            message
          }
        }
      }
    """
    variables = {
        "input": {
            "token": token,
            "password": "new_password",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["resetPassword"]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_invalid_input(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    token = create_reset_password_token(
        auth_private_key,
        UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        "hashed_password",
    )
    query = """
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              __typename
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "token": token,
            "password": "p",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert data["__typename"] == "InvalidInputProblem"


@pytest.mark.anyio()
async def test_reset_password_invalid_token(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              ... on InvalidResetPasswordTokenProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "token": "invalid-token",
            "password": "new_password",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_user_not_found(
    auth_private_key: str, client: AsyncClient, graphql_url: str
) -> None:
    token = create_reset_password_token(
        auth_private_key,
        UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        "hashed_password",
    )
    query = """
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              ... on InvalidResetPasswordTokenProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "token": token,
            "password": "new_password",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_reset_password_invalid_fingerprint_same_token_used_twice(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_user(db)
    token = create_reset_password_token(auth_private_key, user.id, user.hashed_password)
    query = """
      mutation ResetPassword($input: ResetPasswordInput!) {
        resetPassword(input: $input) {
          ... on ResetPasswordFailure {
            problems {
              ... on InvalidResetPasswordTokenProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "token": token,
            "password": "new_password",
        }
    }

    await client.post(graphql_url, json={"query": query, "variables": variables})
    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["resetPassword"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_change_my_password(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(
        db, hashed_password=hash_password("plain_password")
    )
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation ChangeMyPassword($input: ChangeMyPasswordInput!) {
        changeMyPassword(input: $input) {
          ... on ChangeMyPasswordSuccess {
            message
          }
        }
      }
    """
    variables = {
        "input": {
            "currentPassword": "plain_password",
            "newPassword": "new_password",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["changeMyPassword"]
    assert "message" in data


@pytest.mark.anyio()
async def test_change_my_password_invalid_input(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(db)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation ChangeMyPassword($input: ChangeMyPasswordInput!) {
        changeMyPassword(input: $input) {
          ... on ChangeMyPasswordFailure {
            problems {
              __typename
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "currentPassword": "plain_password",
            "newPassword": "p",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["changeMyPassword"]["problems"][0]
    assert data["__typename"] == "InvalidInputProblem"


@pytest.mark.anyio()
async def test_change_my_password_invalid_password(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(
        db, hashed_password=hash_password("plain_password")
    )
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation ChangeMyPassword($input: ChangeMyPasswordInput!) {
        changeMyPassword(input: $input) {
          ... on ChangeMyPasswordFailure {
            problems {
              ... on InvalidPasswordProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "currentPassword": "invalid_password",
            "newPassword": "new_password",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["changeMyPassword"]["problems"][0]
    assert "message" in data
