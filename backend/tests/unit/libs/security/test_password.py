import pytest

from backend.libs.security.password import (
    async_hash_password,
    async_verify_and_update_password,
    hash_password,
    verify_and_update_password,
)
from tests.unit.helpers.async_executor import run_without_executor


def test_hashed_password_is_properly_verified() -> None:
    plain_password = "plain_password"

    hashed_password = hash_password(plain_password)
    verfied_password, _ = verify_and_update_password(plain_password, hashed_password)

    assert verfied_password


@pytest.mark.anyio()
async def test_async_hashed_password_is_properly_verified() -> None:
    plain_password = "plain_password"

    hashed_password = await async_hash_password(plain_password, run_without_executor)
    verfied_password, _ = await async_verify_and_update_password(
        plain_password, hashed_password, run_without_executor
    )

    assert verfied_password
