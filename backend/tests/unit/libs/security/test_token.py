import pytest

from backend.libs.security.token import (
    InvalidTokenError,
    create_paseto_token_public_v4,
    read_paseto_token_public_v4,
)


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

    token = create_paseto_token_public_v4(
        payload={"sub": "test-sub"},
        expiration=100,
        key=private_key,
    )
    data = read_paseto_token_public_v4(token=token, key=public_key)

    assert data["sub"] == "test-sub"
    assert "exp" in data
    assert "iat" in data


def test_read_paseto_token_invalid_token() -> None:
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

    token = create_paseto_token_public_v4(
        payload={"sub": "test-sub"},
        expiration=100,
        key=private_key,
    )

    with pytest.raises(InvalidTokenError):
        read_paseto_token_public_v4(token=token.lower(), key=public_key)
