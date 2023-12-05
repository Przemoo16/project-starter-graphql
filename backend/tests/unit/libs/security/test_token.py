import pytest

from backend.libs.security.token import (
    InvalidTokenError,
    async_create_paseto_token_public_v4,
    async_read_paseto_token_public_v4,
    create_paseto_token_public_v4,
    read_paseto_token_public_v4,
)
from tests.unit.helpers.async_executor import run_without_executor


def test_create_and_read_paseto_token() -> None:
    private_key = (
        b"-----BEGIN PRIVATE KEY-----\n"
        b"MC4CAQAwBQYDK2VwBCIEICT9X3zKdFe6HxcwF1oisi7s0nLxwCTEDfhLfau7Vvsm\n"
        b"-----END PRIVATE KEY-----\n"
    )
    public_key = (
        b"-----BEGIN PUBLIC KEY-----\n"
        b"MCowBQYDK2VwAyEAKFjjyzUcQaSCom09ZZCNuIVqAreu03jRa72OLvmSkWI=\n"
        b"-----END PUBLIC KEY-----\n"
    )

    token = create_paseto_token_public_v4({"sub": "test-sub"}, 100, private_key)
    data = read_paseto_token_public_v4(token, public_key)

    assert data["sub"] == "test-sub"
    assert "exp" in data
    assert "iat" in data


def test_read_paseto_raises_exception_if_token_is_invalid() -> None:
    private_key = (
        b"-----BEGIN PRIVATE KEY-----\n"
        b"MC4CAQAwBQYDK2VwBCIEICT9X3zKdFe6HxcwF1oisi7s0nLxwCTEDfhLfau7Vvsm\n"
        b"-----END PRIVATE KEY-----\n"
    )
    public_key = (
        b"-----BEGIN PUBLIC KEY-----\n"
        b"MCowBQYDK2VwAyEAKFjjyzUcQaSCom09ZZCNuIVqAreu03jRa72OLvmSkWI=\n"
        b"-----END PUBLIC KEY-----\n"
    )

    token = create_paseto_token_public_v4({"sub": "test-sub"}, 100, private_key)

    with pytest.raises(InvalidTokenError):
        read_paseto_token_public_v4(token.lower(), public_key)


@pytest.mark.anyio()
async def test_async_create_and_read_paseto_token() -> None:
    private_key = (
        b"-----BEGIN PRIVATE KEY-----\n"
        b"MC4CAQAwBQYDK2VwBCIEICT9X3zKdFe6HxcwF1oisi7s0nLxwCTEDfhLfau7Vvsm\n"
        b"-----END PRIVATE KEY-----\n"
    )
    public_key = (
        b"-----BEGIN PUBLIC KEY-----\n"
        b"MCowBQYDK2VwAyEAKFjjyzUcQaSCom09ZZCNuIVqAreu03jRa72OLvmSkWI=\n"
        b"-----END PUBLIC KEY-----\n"
    )

    token = await async_create_paseto_token_public_v4(
        {"sub": "test-sub"}, 100, private_key, run_without_executor
    )
    data = await async_read_paseto_token_public_v4(
        token, public_key, run_without_executor
    )

    assert data["sub"] == "test-sub"
    assert "exp" in data
    assert "iat" in data
