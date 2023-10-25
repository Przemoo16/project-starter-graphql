from dataclasses import dataclass
from datetime import datetime
from functools import partial
from uuid import UUID

from backend.libs.db.crud import CRUD, UNSET, UnsetType
from backend.services.user.models import User


@dataclass
class UserCreateData:
    email: str
    hashed_password: str
    full_name: str


@dataclass
class UserUpdateData:
    email: str | UnsetType = UNSET
    hashed_password: str | UnsetType = UNSET
    full_name: str | UnsetType = UNSET
    confirmed_email: bool | UnsetType = UNSET
    last_login: datetime | UnsetType = UNSET


@dataclass
class UserFilters:
    id: UUID | UnsetType = UNSET
    email: str | UnsetType = UNSET


UserCRUD = partial(CRUD[User, UserCreateData, UserUpdateData, UserFilters], User)
