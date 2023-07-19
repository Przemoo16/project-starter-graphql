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
    payload = {
        "query": """
            mutation {
              createUser(input: {email: "test@email.com", password: "plain_password"}) {
                ... on User {
                  id
                  email
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]
    assert "id" in data
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_invalid_input(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              createUser(input: {email: "test", password: "plain_password"}) {
                ... on CreateUserFailure {
                  problems {
                    __typename
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["createUser"]["problems"][0]
    assert data["__typename"] == "InvalidInputProblem"


@pytest.mark.anyio()
async def test_create_user_already_exists(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(session, email="test@email.com")
    payload = {
        "query": """
            mutation {
              createUser(input: {email: "test@email.com", password: "plain_password"}) {
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
    }

    response = await async_client.post("/graphql", json=payload)

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
    payload = {
        "query": """
            query {
              me {
                id
                email
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload, headers=auth_header)

    data = response.json()["data"]["me"]
    assert data == {
        "id": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
        "email": "test@email.com",
    }
