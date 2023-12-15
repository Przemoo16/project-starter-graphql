from uuid import UUID

import pytest

from tests.integration.conftest import AsyncClient, AsyncSession
from tests.integration.helpers.user import (
    create_auth_header,
    create_confirmed_user,
    create_user,
)


@pytest.mark.anyio()
async def test_create_user_returns_created_user(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on User {
            id
            email
            fullName
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "plain_password",
            "fullName": "Test User",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["createUser"]
    assert "id" in data
    assert data["email"] == "test@email.com"
    assert data["fullName"] == "Test User"


@pytest.mark.anyio()
async def test_create_user_returns_problem_if_email_is_invalid(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test",
            "password": "plain_password",
            "fullName": "Test User",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    assert response.json()["data"]["createUser"]["problems"] == [{"path": ["email"]}]


@pytest.mark.anyio()
async def test_create_user_returns_problem_if_password_is_too_short(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "p",
            "fullName": "Test User",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    assert response.json()["data"]["createUser"]["problems"] == [{"path": ["password"]}]


@pytest.mark.anyio()
async def test_create_user_returns_problem_if_full_name_is_too_short(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "plain_password",
            "fullName": "",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    assert response.json()["data"]["createUser"]["problems"] == [{"path": ["fullName"]}]


@pytest.mark.anyio()
async def test_create_user_returns_problem_if_full_name_is_too_long(
    client: AsyncClient, graphql_url: str
) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "plain_password",
            "fullName": "T" * 129,
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    assert response.json()["data"]["createUser"]["problems"] == [{"path": ["fullName"]}]


@pytest.mark.anyio()
async def test_create_user_returns_problem_if_user_already_exists(
    db: AsyncSession, client: AsyncClient, graphql_url: str
) -> None:
    await create_user(db, email="test@email.com")
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              ... on UserAlreadyExistsProblem {
                message
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "plain_password",
            "fullName": "Test User",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}
    )

    problems = response.json()["data"]["createUser"]["problems"]
    assert len(problems) == 1
    assert "message" in problems[0]


@pytest.mark.anyio()
async def test_get_me_returns_user(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(
        db, id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    )
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      query GetMe {
        me {
          id
        }
      }
    """

    response = await client.post(
        graphql_url, json={"query": query}, headers=auth_header
    )

    data = response.json()["data"]["me"]
    assert data == {
        "id": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
    }


@pytest.mark.anyio()
async def test_update_me_returns_updated_user(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(db, full_name="Test User")
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on User {
            fullName
          }
        }
      }
    """
    variables = {
        "input": {
            "fullName": "Updated User",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["updateMe"]
    assert data == {
        "fullName": "Updated User",
    }


@pytest.mark.anyio()
async def test_update_me_returns_problem_if_full_name_is_too_short(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(db)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on UpdateMeFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "fullName": "",
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    assert response.json()["data"]["updateMe"]["problems"] == [{"path": ["fullName"]}]


@pytest.mark.anyio()
async def test_update_me_returns_problem_if_full_name_is_too_long(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(db)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on UpdateMeFailure {
            problems {
              ... on InvalidInputProblem {
                path
              }
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "fullName": "T" * 129,
        }
    }

    response = await client.post(
        graphql_url, json={"query": query, "variables": variables}, headers=auth_header
    )

    assert response.json()["data"]["updateMe"]["problems"] == [{"path": ["fullName"]}]


@pytest.mark.anyio()
async def test_delete_me_returns_success_message(
    db: AsyncSession,
    auth_private_key: str,
    client: AsyncClient,
    graphql_url: str,
) -> None:
    user = await create_confirmed_user(db)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation DeleteMe {
        deleteMe {
          message
        }
      }
    """

    response = await client.post(
        graphql_url, json={"query": query}, headers=auth_header
    )

    data = response.json()["data"]["deleteMe"]
    assert "message" in data
