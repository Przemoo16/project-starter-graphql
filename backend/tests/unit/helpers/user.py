from typing import Any
from uuid import uuid4

from backend.services.user.models import User


def create_confirmed_user(**kwargs: Any) -> User:
    kwargs["confirmed_email"] = True
    return create_user(**kwargs)


def create_user(**kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = f"{uuid4()}@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "hashed_password"
    return User(**kwargs)
