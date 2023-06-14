from dataclasses import dataclass

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import instance_state

from backend.crud.base import BaseCRUD, NoObjectFoundError
from backend.models.base import Base
from backend.types.scalars import UNSET


class Test(Base):
    __tablename__ = "test"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default="Test User")
    age: Mapped[int] = mapped_column(default=25)


@dataclass
class TestCreate:
    id: int = 1
    name: str = "Created User"


@dataclass
class TestUpdate:
    name: str = UNSET
    age: int = UNSET


@dataclass
class TestFilters:
    id: int = UNSET
    name: str = UNSET


CRUD = BaseCRUD[Test, TestCreate, TestUpdate, TestFilters]


@pytest.fixture(name="crud")
def crud_fixture(session: AsyncSession) -> CRUD:
    return CRUD(model=Test, session=session)


@pytest.mark.anyio()
async def test_create(crud: CRUD, session: AsyncSession) -> None:
    data = TestCreate(id=1, name="Created User")

    await crud.create(data)

    retrieved_obj = await session.get(Test, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Created User"


@pytest.mark.anyio()
async def test_create_no_refresh(crud: CRUD) -> None:
    data = TestCreate()

    db_obj = await crud.create(data)

    assert instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_create_refresh(crud: CRUD) -> None:
    data = TestCreate()

    db_obj = await crud.create_and_refresh(data)

    assert not instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_read_one(crud: CRUD, session: AsyncSession) -> None:
    session.add(Test(id=1))
    await session.commit()
    filters = TestFilters(id=1)

    db_obj = await crud.read_one(filters)

    assert db_obj.id == 1


@pytest.mark.anyio()
async def test_read_one_not_found(crud: CRUD, session: AsyncSession) -> None:
    session.add(Test(id=1))
    await session.commit()
    filters = TestFilters(id=2)

    with pytest.raises(NoObjectFoundError):
        await crud.read_one(filters)


@pytest.mark.anyio()
async def test_update(crud: CRUD, session: AsyncSession) -> None:
    initial_obj = Test(id=1, name="Test User", age=25)
    session.add(initial_obj)
    await session.commit()
    data = TestUpdate(name="Updated User")

    await crud.update(initial_obj, data)

    retrieved_obj = await session.get(Test, 1)
    assert retrieved_obj
    assert retrieved_obj.name == "Updated User"
    assert retrieved_obj.age == 25


@pytest.mark.anyio()
async def test_update_no_refresh(crud: CRUD) -> None:
    data = TestUpdate()

    db_obj = await crud.update(Test(), data)

    assert instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_update_and_refresh(crud: CRUD) -> None:
    data = TestUpdate()

    db_obj = await crud.update_and_refresh(Test(), data)

    assert not instance_state(db_obj).expired


@pytest.mark.anyio()
async def test_delete(crud: CRUD, session: AsyncSession) -> None:
    initial_obj = Test(id=1)
    session.add(initial_obj)
    await session.commit()

    await crud.delete(initial_obj)

    assert not await session.get(Test, 1)
