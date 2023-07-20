from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_auth_header,
    create_confirmed_user,
    create_user,
)


@pytest.mark.anyio()
async def test_create_user(async_client: AsyncClient) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on User {
            id
            email
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test@email.com",
            "password": "plain_password",
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["createUser"]
    assert "id" in data
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_invalid_input(async_client: AsyncClient) -> None:
    query = """
      mutation CreateUser($input: UserCreateInput!) {
        createUser(input: $input) {
          ... on CreateUserFailure {
            problems {
              __typename
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test",
            "password": "plain_password",
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["createUser"]["problems"][0]
    assert data["__typename"] == "InvalidInputProblem"


@pytest.mark.anyio()
async def test_create_user_already_exists(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(session, email="test@email.com")
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
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()["data"]["createUser"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_get_me(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(
        session, id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
    )
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      query GetMe {
        me {
          id
          email
        }
      }
    """

    response = await async_client.post(
        "/graphql", json={"query": query}, headers=auth_header
    )

    data = response.json()["data"]["me"]
    assert data == {
        "id": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
        "email": "test@email.com",
    }


@pytest.mark.anyio()
async def test_update_me(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(
        session, id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
    )
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on User {
            id
            email
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "updated@email.com",
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["updateMe"]
    assert data == {
        "id": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
        "email": "updated@email.com",
    }


@pytest.mark.anyio()
async def test_update_me_invalid_input(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(session)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on UpdateMeFailure {
            problems {
              __typename
            }
          }
        }
      }
    """
    variables = {
        "input": {
            "email": "test",
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["updateMe"]["problems"][0]
    assert data["__typename"] == "InvalidInputProblem"


@pytest.mark.anyio()
async def test_update_me_user_with_provided_email_already_exists(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    await create_user(session, email="updated@email.com")
    user = await create_confirmed_user(session, email="test@email.com")
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation UpdateMe($input: UpdateMeInput!) {
        updateMe(input: $input) {
          ... on UpdateMeFailure {
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
            "email": "updated@email.com",
        }
    }

    response = await async_client.post(
        "/graphql", json={"query": query, "variables": variables}, headers=auth_header
    )

    data = response.json()["data"]["updateMe"]["problems"][0]
    assert "message" in data


@pytest.mark.anyio()
async def test_delete_me(
    session: AsyncSession, auth_private_key: str, async_client: AsyncClient
) -> None:
    user = await create_confirmed_user(session)
    auth_header = create_auth_header(auth_private_key, user.id)
    query = """
      mutation DeleteMe {
        deleteMe {
          message
        }
      }
    """

    response = await async_client.post(
        "/graphql", json={"query": query}, headers=auth_header
    )

    data = response.json()["data"]["deleteMe"]
    assert "message" in data
