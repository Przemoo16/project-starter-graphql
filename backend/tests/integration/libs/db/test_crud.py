import pytest
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import instance_state

from backend.libs.db.crud import CRUD, NoObjectFoundError
from tests.integration.conftest import Base
from tests.integration.helpers.db import save_to_db


class Dummy(Base):
    __tablename__ = "test"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default="Test")
    age: Mapped[int] = mapped_column(default=25)


class DummyCreate(BaseModel):
    id: int = 1
    name: str = "Created"


class DummyUpdate(BaseModel):
    name: str | None = None
    age: int | None = None


class DummyFilters(BaseModel):
    id: int | None = None
    name: str | None = None


DummyCRUD = CRUD[Dummy, DummyCreate, DummyUpdate, DummyFilters]


@pytest.fixture(name="crud")
def crud_fixture(session: AsyncSession) -> DummyCRUD:
    return DummyCRUD(model=Dummy, session=session)


@pytest.mark.anyio()
async def test_create(crud: DummyCRUD, session: AsyncSession) -> None:
    data = DummyCreate(id=1, name="Created")

    await crud.create(data)

    retrieved_obj = await session.get(Dummy, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Created"


@pytest.mark.anyio()
async def test_create_no_refresh(crud: DummyCRUD) -> None:
    data = DummyCreate()

    db_obj = await crud.create(data)

    assert instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_create_and_refresh(crud: DummyCRUD) -> None:
    data = DummyCreate()

    db_obj = await crud.create_and_refresh(data)

    assert not instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_read_one(crud: DummyCRUD, session: AsyncSession) -> None:
    await save_to_db(session, Dummy(id=1))
    filters = DummyFilters(id=1)

    db_obj = await crud.read_one(filters)

    assert db_obj.id == 1


@pytest.mark.anyio()
async def test_read_one_object_not_found(
    crud: DummyCRUD, session: AsyncSession
) -> None:
    await save_to_db(session, Dummy(id=1))
    filters = DummyFilters(id=2)

    with pytest.raises(NoObjectFoundError):
        await crud.read_one(filters)


@pytest.mark.anyio()
async def test_update(crud: DummyCRUD, session: AsyncSession) -> None:
    initial_obj = Dummy(id=1, name="Test", age=25)
    await save_to_db(session, initial_obj)
    data = DummyUpdate(name="Updated")

    await crud.update(initial_obj, data)

    retrieved_obj = await session.get(Dummy, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Updated"
    assert retrieved_obj.age == 25


@pytest.mark.anyio()
async def test_update_no_refresh(crud: DummyCRUD) -> None:
    data = DummyUpdate()
    obj = Dummy()

    db_obj = await crud.update(obj, data)

    assert instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_update_and_refresh(crud: DummyCRUD) -> None:
    data = DummyUpdate()
    obj = Dummy()

    db_obj = await crud.update_and_refresh(obj, data)

    assert not instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_delete(crud: DummyCRUD, session: AsyncSession) -> None:
    initial_obj = Dummy(id=1)
    await save_to_db(session, initial_obj)

    await crud.delete(initial_obj)

    assert not await session.get(Dummy, 1)
