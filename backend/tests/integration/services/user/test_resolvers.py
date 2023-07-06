from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_email_confirmation_token,
    create_user,
    hash_password,
)


@pytest.mark.anyio()
async def test_create_user(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              createUser(input: {email: "test@email.com", password: "plain_password"}) {
                ... on CreateUserSuccess {
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
    assert data["__typename"] == "InvalidInput"


@pytest.mark.anyio()
async def test_create_user_already_exists(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(session, email="test@email.com")
    payload = {
        "query": """
            mutation {
              createUser(input: {email: "test@email.com", password: "plain_password"}) {
                ... on CreateUserFailure {
                  problems {
                    ... on UserAlreadyExists {
                      message
                      email
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
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_confirm_email(
    async_client: AsyncClient, session: AsyncSession, auth_private_key: str
) -> None:
    user = await create_user(
        session,
        id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        email="test@email.com",
        confirmed_email=False,
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
async def test_confirm_email_invalid_token(
    async_client: AsyncClient, auth_private_key: str
) -> None:
    token = create_email_confirmation_token(
        auth_private_key, UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), "test@email.com"
    )
    payload = {
        "query": f"""
            mutation {{
              confirmEmail(token: "{token}") {{
                ... on ConfirmEmailFailure {{
                  problems {{
                    ... on InvalidEmailConfirmationToken {{
                      message
                      token
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
    assert data["token"] == token


@pytest.mark.anyio()
async def test_confirm_email_already_confirmed(
    async_client: AsyncClient, session: AsyncSession, auth_private_key: str
) -> None:
    user = await create_user(
        session,
        id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        email="test@email.com",
        confirmed_email=True,
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
                      email
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
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_login(async_client: AsyncClient, session: AsyncSession) -> None:
    await create_user(
        session,
        email="test@email.com",
        hashed_password=hash_password("plain_password"),
        confirmed_email=True,
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginSuccess {
                  accessToken
                  refreshToken
                  tokenType
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["tokenType"] == "Bearer"


@pytest.mark.anyio()
async def test_login_invalid_credentials(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(
        session,
        email="test@email.com",
        hashed_password=hash_password("plain_password"),
        confirmed_email=True,
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "invalid_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on InvalidCredentials {
                      message
                      username
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data
    assert data["username"] == "test@email.com"


@pytest.mark.anyio()
async def test_login_user_not_confirmed(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(
        session,
        email="test@email.com",
        hashed_password=hash_password("plain_password"),
        confirmed_email=False,
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on UserNotConfirmed {
                      message
                      username
                    }
                  }
                }
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["login"]["problems"][0]
    assert "message" in data
    assert data["username"] == "test@email.com"


@pytest.mark.anyio()
async def test_reset_password(async_client: AsyncClient, session: AsyncSession) -> None:
    await create_user(
        session,
        email="test@email.com",
        confirmed_email=True,
    )
    payload = {
        "query": """
            mutation {
              resetPassword(email: "test@email.com") {
                message
                email
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]
    assert "message" in data
    assert data["email"] == "test@email.com"


@pytest.mark.anyio()
async def test_reset_password_user_not_exists(async_client: AsyncClient) -> None:
    payload = {
        "query": """
            mutation {
              resetPassword(email: "test@email.com") {
                message
                email
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]
    assert data


@pytest.mark.anyio()
async def test_reset_password_user_not_confirmed(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    await create_user(
        session,
        email="test@email.com",
        confirmed_email=False,
    )
    payload = {
        "query": """
            mutation {
              resetPassword(email: "test@email.com") {
                message
                email
              }
            }
        """
    }

    response = await async_client.post("/graphql", json=payload)

    data = response.json()["data"]["resetPassword"]
    assert data
