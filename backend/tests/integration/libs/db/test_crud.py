from dataclasses import dataclass

import pytest
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import instance_state

from backend.libs.db.crud import CRUD, UNSET, NoObjectFoundError, UnsetType
from tests.integration.conftest import AsyncSession, Base
from tests.integration.helpers.db import save_to_db


class Dummy(Base):
    __tablename__ = "test"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default="Test")
    age: Mapped[int] = mapped_column(default=25)


@dataclass
class DummyCreate:
    id: int = 1
    name: str = "Created"


@dataclass
class DummyUpdate:
    name: str | UnsetType = UNSET
    age: int | UnsetType = UNSET


@dataclass
class DummyFilters:
    id: int | UnsetType = UNSET
    name: str | UnsetType = UNSET


DummyCRUD = CRUD[Dummy, DummyCreate, DummyUpdate, DummyFilters]


@pytest.fixture(name="crud")
def crud_fixture(db: AsyncSession) -> DummyCRUD:
    return DummyCRUD(model=Dummy, db=db)


@pytest.mark.anyio()
async def test_create_creates_entry_in_db(crud: DummyCRUD, db: AsyncSession) -> None:
    data = DummyCreate(id=1, name="Created")

    await crud.create(data)

    retrieved_obj = await db.get(Dummy, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Created"


@pytest.mark.anyio()
async def test_create_and_refresh_refreshes_db_object(crud: DummyCRUD) -> None:
    data = DummyCreate()

    db_obj = await crud.create_and_refresh(data)

    assert not instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_read_one_retrieves_entry_from_db(
    crud: DummyCRUD, db: AsyncSession
) -> None:
    await save_to_db(db, Dummy(id=1))
    filters = DummyFilters(id=1)

    db_obj = await crud.read_one(filters)

    assert db_obj.id == 1


@pytest.mark.anyio()
async def test_read_one_raises_exception_if_entry_in_db_is_not_found(
    crud: DummyCRUD, db: AsyncSession
) -> None:
    await save_to_db(db, Dummy(id=1))
    filters = DummyFilters(id=2)

    with pytest.raises(NoObjectFoundError):
        await crud.read_one(filters)


@pytest.mark.anyio()
async def test_update_updates_entry_in_db(crud: DummyCRUD, db: AsyncSession) -> None:
    initial_obj = Dummy(id=1, name="Test", age=25)
    await save_to_db(db, initial_obj)
    data = DummyUpdate(name="Updated")

    await crud.update(initial_obj, data)

    retrieved_obj = await db.get(Dummy, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Updated"
    assert retrieved_obj.age == 25  # noqa: PLR2004


@pytest.mark.anyio()
async def test_update_expires_db_object(crud: DummyCRUD) -> None:
    data = DummyUpdate()
    obj = Dummy()

    await crud.update(obj, data)

    assert instance_state(obj).expired


@pytest.mark.anyio()
async def test_update_and_refresh_refreshes_db_object(crud: DummyCRUD) -> None:
    data = DummyUpdate()
    obj = Dummy()

    await crud.update_and_refresh(obj, data)

    assert not instance_state(obj).expired


@pytest.mark.anyio()
async def test_delete_deletes_entry_from_db(crud: DummyCRUD, db: AsyncSession) -> None:
    initial_obj = Dummy(id=1)
    await save_to_db(db, initial_obj)

    await crud.delete(initial_obj)

    assert not await db.get(Dummy, 1)
