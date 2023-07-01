from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Select, select

Model = TypeVar("Model", bound=DeclarativeBase)
CreateData_contra = TypeVar("CreateData_contra", bound=BaseModel, contravariant=True)
UpdateData_contra = TypeVar("UpdateData_contra", bound=BaseModel, contravariant=True)
Filters_contra = TypeVar("Filters_contra", bound=BaseModel, contravariant=True)


class NoObjectFoundError(Exception):
    pass


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


class CRUD(Generic[Model, CreateData_contra, UpdateData_contra, Filters_contra]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, data: CreateData_contra) -> Model:
        created_obj = self._create_obj(data)
        return await self._commit(created_obj)

    async def create_and_refresh(self, data: CreateData_contra) -> Model:
        created_obj = self._create_obj(data)
        return await self._commit_and_refresh(created_obj)

    def _create_obj(self, data: CreateData_contra) -> Model:
        data_dict = data.model_dump()
        return self.model(**data_dict)

    async def read_one(self, filters: Filters_contra) -> Model:
        statement = self._build_where_statement(select(self.model), filters)
        result = await self.session.execute(statement)
        try:
            return result.scalars().one()
        except NoResultFound as exc:
            raise NoObjectFoundError from exc

    async def update(self, obj: Model, data: UpdateData_contra) -> Model:
        updated_obj = self._update_obj(obj, data)
        return await self._commit(updated_obj)

    async def update_and_refresh(self, obj: Model, data: UpdateData_contra) -> Model:
        updated_obj = self._update_obj(obj, data)
        return await self._commit_and_refresh(updated_obj)

    def _update_obj(self, obj: Model, data: UpdateData_contra) -> Model:
        data_dict = data.model_dump(exclude_unset=True)
        for field, value in data_dict.items():
            setattr(obj, field, value)
        return obj

    async def delete(self, obj: Model) -> None:
        await self.session.delete(obj)
        await self.session.commit()

    async def _commit(self, obj: Model) -> Model:
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def _commit_and_refresh(self, obj: Model) -> Model:
        obj = await self._commit(obj)
        await self.session.refresh(obj)
        return obj

    def _build_where_statement(
        self, statement: Select[tuple[Model]], filters: Filters_contra
    ) -> Select[tuple[Model]]:
        filters_dict = filters.model_dump(exclude_unset=True)
        for field, value in filters_dict.items():
            statement = statement.where(getattr(self.model, field) == value)
        return statement
