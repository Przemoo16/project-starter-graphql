import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import create_user, hash_password


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
async def test_login_last_login_updated(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = await create_user(
        session,
        email="test@email.com",
        hashed_password=hash_password("plain_password"),
        confirmed_email=True,
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                __typename
              }
            }
        """
    }

    await async_client.post("/graphql", json=payload)

    assert user.last_login


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
