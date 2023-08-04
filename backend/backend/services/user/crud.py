from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from backend.libs.db.crud import CRUD, CRUDProtocol
from backend.services.user.models import User


class UserCreateData(BaseModel):
    email: str
    hashed_password: str
    full_name: str


class UserUpdateData(BaseModel):
    email: str | None = None
    hashed_password: str | None = None
    full_name: str | None = None
    confirmed_email: bool | None = None
    last_login: datetime | None = None


class UserFilters(BaseModel):
    id: UUID | None = None
    email: str | None = None


UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]
