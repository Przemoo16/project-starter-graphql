from dataclasses import dataclass

import strawberry

from backend.libs.types.scalars import UNSET


@strawberry.type
class UserCreate:
    email: str
    password: str
    full_name: str


@dataclass
class UserUpdate:
    email: str = UNSET
    password: str = UNSET
    full_name: str = UNSET
    confirmed_email: bool = UNSET


@strawberry.type
class UserFilters:
    email: str = UNSET
