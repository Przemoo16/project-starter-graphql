import pytest

from backend.libs.api.headers import BearerTokenNotFoundError, read_bearer_token


def test_read_bearer_token() -> None:
    headers = {"Authorization": "Bearer test-token"}

    token = read_bearer_token(headers)

    assert token == "test-token"


def test_read_bearer_token_missing_auth_header() -> None:
    headers = {"Content-Type": "application/json"}

    with pytest.raises(BearerTokenNotFoundError):
        read_bearer_token(headers)


def test_read_bearer_token_invalid_header() -> None:
    headers = {"Authorization": "invalid-token"}

    with pytest.raises(BearerTokenNotFoundError):
        read_bearer_token(headers)


def test_read_bearer_token_not_bearer_token() -> None:
    headers = {"Authorization": "Unknown test-token"}

    with pytest.raises(BearerTokenNotFoundError):
        read_bearer_token(headers)
