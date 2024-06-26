from dataclasses import asdict
from typing import Generic, Protocol, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Select, select

from backend.libs.db.session import AsyncSession
from backend.libs.types.dataclass import Dataclass
from backend.libs.types.unset import is_unset

Model = TypeVar("Model", bound=DeclarativeBase)
CreateData_contra = TypeVar("CreateData_contra", bound=Dataclass, contravariant=True)
UpdateData_contra = TypeVar("UpdateData_contra", bound=Dataclass, contravariant=True)
Filters_contra = TypeVar("Filters_contra", bound=Dataclass, contravariant=True)


class NoObjectFoundError(Exception):
    pass


class CRUDProtocol(
    Protocol[Model, CreateData_contra, UpdateData_contra, Filters_contra]
):
    async def create(self, data: CreateData_contra) -> None:
        ...

    async def create_and_refresh(self, data: CreateData_contra) -> Model:
        ...

    async def read_one(self, filters: Filters_contra) -> Model:
        ...

    async def update(self, obj: Model, data: UpdateData_contra) -> None:
        ...

    async def update_and_refresh(self, obj: Model, data: UpdateData_contra) -> None:
        ...

    async def delete(self, obj: Model) -> None:
        ...


class CRUD(Generic[Model, CreateData_contra, UpdateData_contra, Filters_contra]):
    def __init__(self, model: type[Model], db: AsyncSession):
        self._model = model
        self._db = db

    async def create(self, data: CreateData_contra) -> None:
        created_obj = self._create_obj(data)
        await self._commit(created_obj)

    async def create_and_refresh(self, data: CreateData_contra) -> Model:
        created_obj = self._create_obj(data)
        await self._commit_and_refresh(created_obj)
        return created_obj

    def _create_obj(self, data: CreateData_contra) -> Model:
        data_dict = asdict(data)
        return self._model(**data_dict)

    async def read_one(self, filters: Filters_contra) -> Model:
        statement = self._build_where_statement(select(self._model), filters)
        result = await self._db.execute(statement)
        try:
            return result.scalars().one()
        except NoResultFound as exc:
            raise NoObjectFoundError from exc

    async def update(self, obj: Model, data: UpdateData_contra) -> None:
        updated_obj = self._update_obj(obj, data)
        await self._commit(updated_obj)

    async def update_and_refresh(self, obj: Model, data: UpdateData_contra) -> None:
        updated_obj = self._update_obj(obj, data)
        await self._commit_and_refresh(updated_obj)

    def _update_obj(self, obj: Model, data: UpdateData_contra) -> Model:
        data_dict = asdict(data)
        for field, value in data_dict.items():
            if is_unset(value):
                continue
            setattr(obj, field, value)
        return obj

    async def delete(self, obj: Model) -> None:
        await self._db.delete(obj)
        await self._db.commit()

    async def _commit(self, obj: Model) -> None:
        self._db.add(obj)
        await self._db.commit()

    async def _commit_and_refresh(self, obj: Model) -> None:
        await self._commit(obj)
        await self._db.refresh(obj)

    def _build_where_statement(
        self, statement: Select[tuple[Model]], filters: Filters_contra
    ) -> Select[tuple[Model]]:
        filters_dict = asdict(filters)
        for field, value in filters_dict.items():
            if is_unset(value):
                continue
            statement = statement.where(getattr(self._model, field) == value)
        return statement
