import uuid
from typing import Any

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.user.models import User
from tests.integration.helpers.db import save_to_db


async def create_user(session: AsyncSession, **kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = f"{uuid.uuid4()}@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "hashed_password"
    user = User(**kwargs)
    return await save_to_db(session, user)


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)
