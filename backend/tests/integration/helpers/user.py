from collections.abc import Mapping
from typing import Any
from uuid import UUID

import orjson
from passlib.context import CryptContext
from pyseto import Key, Paseto

from backend.services.user.models import User
from tests.integration.conftest import AsyncSession
from tests.integration.helpers.db import save_to_db


async def create_confirmed_user(db: AsyncSession, **kwargs: Any) -> User:
    kwargs["confirmed_email"] = True
    return await create_user(db, **kwargs)


async def create_user(db: AsyncSession, **kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = "test_helper_user@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "test_helper_hashed_password"
    if "full_name" not in kwargs:
        kwargs["full_name"] = "Test Helper User"
    user = User(**kwargs)
    return await save_to_db(db, user)


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def create_auth_header(key: str, user_id: UUID) -> dict[str, str]:
    token = create_access_token(key, user_id)
    return {"Authorization": f"Bearer {token}"}


def create_access_token(key: str, user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
    }
    return _create_token(key, payload)


def create_refresh_token(key: str, user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
    }
    return _create_token(key, payload)


def create_email_confirmation_token(key: str, user_id: UUID, user_email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": user_email,
        "type": "email-confirmation",
    }
    return _create_token(key, payload)


def create_reset_password_token(key: str, user_id: UUID, user_password: str) -> str:
    payload = {
        "sub": str(user_id),
        "fingerprint": hash_password(user_password),
        "type": "reset-password",
    }
    return _create_token(key, payload)


def _create_token(key: str, payload: Mapping[str, Any], expiration: int = 10) -> str:
    paseto = Paseto.new(exp=expiration, include_iat=True)
    paseto_key = Key.new(version=4, purpose="public", key=key)
    token = paseto.encode(
        key=paseto_key,
        payload=dict(payload),
        serializer=orjson,
    )
    return token.decode("utf-8")  # type: ignore[no-any-return]
