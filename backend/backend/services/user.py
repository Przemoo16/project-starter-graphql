from backend.crud.base import CRUDProtocol
from backend.models.user import User
from backend.types.user import UserCreate, UserFilters, UserUpdate

UserCRUDProtocol = CRUDProtocol[User, UserCreate, UserUpdate, UserFilters]


async def create_user(data: UserCreate, crud: UserCRUDProtocol) -> User:
    return await crud.create_and_refresh(data)
