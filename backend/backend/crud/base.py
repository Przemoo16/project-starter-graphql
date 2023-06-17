from typing import Protocol

from backend.libs.db.crud import (
    CreateData_contra,
    Filters_contra,
    Model,
    UpdateData_contra,
)


class CRUDProtocol(
    Protocol[Model, CreateData_contra, UpdateData_contra, Filters_contra]
):
    async def create(self, data: CreateData_contra) -> Model:
        ...

    async def create_and_refresh(self, data: CreateData_contra) -> Model:
        ...

    async def read_one(self, filters: Filters_contra) -> Model:
        ...

    async def update(self, obj: Model, data: UpdateData_contra) -> Model:
        ...

    async def update_and_refresh(self, obj: Model, data: UpdateData_contra) -> Model:
        ...

    async def delete(self, obj: Model) -> None:
        ...
