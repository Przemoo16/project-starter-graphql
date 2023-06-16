from dataclasses import asdict
from typing import Generic, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Select, select

from backend.libs.types.dataclass import DataClassProtocol
from backend.libs.types.scalars import is_unset

Model = TypeVar("Model", bound=DeclarativeBase)
CreateData = TypeVar("CreateData", bound=DataClassProtocol)
UpdateData = TypeVar("UpdateData", bound=DataClassProtocol)
Filters = TypeVar("Filters", bound=DataClassProtocol)


class NoObjectFoundError(Exception):
    pass


class BaseCRUD(Generic[Model, CreateData, UpdateData, Filters]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, data: CreateData) -> Model:
        created_obj = self._create_obj(data)
        return await self._commit(created_obj)

    async def create_and_refresh(self, data: CreateData) -> Model:
        created_obj = self._create_obj(data)
        return await self._commit_and_refresh(created_obj)

    def _create_obj(self, data: CreateData) -> Model:
        data_dict = asdict(data)
        return self.model(**data_dict)

    async def read_one(self, filters: Filters) -> Model:
        statement = self._build_where_statement(select(self.model), filters)
        result = await self.session.execute(statement)
        try:
            return result.scalars().one()
        except NoResultFound as exc:
            raise NoObjectFoundError from exc

    async def update(self, obj: Model, data: UpdateData) -> Model:
        updated_obj = self._update_obj(obj, data)
        return await self._commit(updated_obj)

    async def update_and_refresh(self, obj: Model, data: UpdateData) -> Model:
        updated_obj = self._update_obj(obj, data)
        return await self._commit_and_refresh(updated_obj)

    def _update_obj(self, obj: Model, data: UpdateData) -> Model:
        data_dict = asdict(data)
        for field, value in data_dict.items():
            if is_unset(value):
                continue
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
        self, statement: Select[tuple[Model]], filters: Filters
    ) -> Select[tuple[Model]]:
        filters_dict = asdict(filters)
        for field, value in filters_dict.items():
            if is_unset(value):
                continue
            statement = statement.where(getattr(self.model, field) == value)
        return statement
