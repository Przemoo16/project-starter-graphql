from typing import Generic

from backend.libs.db.crud import (
    CreateData_contra,
    Filters_contra,
    Model,
    UpdateData_contra,
)


class CRUDStub(Generic[Model, CreateData_contra, UpdateData_contra, Filters_contra]):
    async def create(self, data: CreateData_contra) -> None:
        raise NotImplementedError

    async def create_and_refresh(self, data: CreateData_contra) -> Model:
        raise NotImplementedError

    async def read_one(self, filters: Filters_contra) -> Model:
        raise NotImplementedError

    async def update(self, obj: Model, data: UpdateData_contra) -> None:
        raise NotImplementedError

    async def update_and_refresh(self, obj: Model, data: UpdateData_contra) -> None:
        raise NotImplementedError

    async def delete(self, obj: Model) -> None:
        raise NotImplementedError
