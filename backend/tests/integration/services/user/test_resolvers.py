from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.helpers.user import (
    create_confirmed_user,
    create_email_confirmation_token,
    create_reset_password_token,
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
    session: AsyncSession, async_client: AsyncClient
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
async def test_confirm_email_already_confirmed(
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


@pytest.mark.anyio()
async def test_login(session: AsyncSession, async_client: AsyncClient) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
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
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_confirmed_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "invalid_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on InvalidCredentials {
                      message
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


@pytest.mark.anyio()
async def test_login_user_not_confirmed(
    session: AsyncSession, async_client: AsyncClient
) -> None:
    await create_user(
        session, email="test@email.com", hashed_password=hash_password("plain_password")
    )
    payload = {
        "query": """
            mutation {
              login(input: {username: "test@email.com", password: "plain_password"}) {
                ... on LoginFailure {
                  problems {
                    ... on UserNotConfirmed {
                      message
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
async def test_recover_password_user_not_exists(async_client: AsyncClient) -> None:
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
