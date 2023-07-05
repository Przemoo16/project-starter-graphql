from typing import Any
from uuid import UUID, uuid4

import orjson
from passlib.context import CryptContext
from pyseto import Key, Paseto
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.user.models import User
from tests.integration.helpers.db import save_to_db


async def create_user(session: AsyncSession, **kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = f"{uuid4()}@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "hashed_password"
    user = User(**kwargs)
    return await save_to_db(session, user)


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def create_email_confirmation_token(
    key: str, user_id: UUID, user_email: str, expiration: int = 10
) -> str:
    paseto = Paseto.new(exp=expiration, include_iat=True)
    paseto_key = Key.new(version=4, purpose="public", key=key)
    token = paseto.encode(
        key=paseto_key,
        payload={
            "sub": str(user_id),
            "email": user_email,
            "type": "email-confirmation",
        },
        serializer=orjson,
    )
    return token.decode("utf-8")  # type: ignore[no-any-return]
