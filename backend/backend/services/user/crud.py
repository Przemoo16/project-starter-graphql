from backend.libs.db.crud import CRUD, CRUDProtocol
from backend.services.user.models import User
from backend.services.user.schemas import (
    UserCreateData,
    UserFilters,
    UserUpdateData,
)

UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]

UserCRUD = CRUD[User, UserCreateData, UserUpdateData, UserFilters]
