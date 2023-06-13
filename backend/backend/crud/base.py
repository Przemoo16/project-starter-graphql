from dataclasses import asdict
from typing import Generic, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, select

from backend.models.base import Base
from backend.types.dataclass import DataClassProtocol
from backend.types.scalars import is_unset

Model = TypeVar("Model", bound=Base)
CreateData = TypeVar("CreateData", bound=DataClassProtocol)
UpdateData = TypeVar("UpdateData", bound=DataClassProtocol)
Filters = TypeVar("Filters", bound=DataClassProtocol)


class NoObjectFoundError(Exception):
    pass


class BaseCRUD(Generic[Model, CreateData, UpdateData, Filters]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, data: CreateData, refresh: bool = False) -> Model:
        obj = self.model(**asdict(data))
        return await self._add_to_db(obj, refresh)

    async def read_one(self, filters: Filters) -> Model:
        statement = self._build_where_statement(select(self.model), filters)
        result = await self.session.execute(statement)
        try:
            return result.scalars().one()
        except NoResultFound as exc:
            raise NoObjectFoundError from exc

    async def update(
        self, obj: Model, data: UpdateData, refresh: bool = False
    ) -> Model:
        data_dict = asdict(data)
        for field, value in data_dict.items():
            if is_unset(value):
                continue
            setattr(obj, field, value)
        return await self._add_to_db(obj, refresh)

    async def delete(self, obj: Model) -> None:
        await self.session.delete(obj)
        await self.session.commit()

    async def _add_to_db(self, obj: Model, refresh: bool = False) -> Model:
        self.session.add(obj)
        await self.session.commit()
        if refresh:
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
