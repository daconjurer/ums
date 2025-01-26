import uuid

import pytest
from pydantic import Field
from sqlmodel import Field as SQLModelField

from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from ums.core.exceptions import CoreException
from ums.core.filter_sort import BaseFilterParams, SortOptions, SortParams
from ums.domain.data_access.interfaces import Schema
from ums.domain.data_access.reader import GenericReader
from ums.domain.data_access.writer import GenericWriter
from ums.domain.entities import Base


class ABModel(Base, table=True):
    id: uuid.UUID = SQLModelField(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    a: int
    b: int
    is_active: bool = True
    is_deleted: bool = False


class ABModelCreate(Schema):
    a: int
    b: int


class ABModelUpdate(Schema):
    a: int
    b: int


class ABModelFilter(BaseFilterParams):
    a: int | None = Field(
        default=None,
        examples=[""],
        description="Value of the a field",
    )
    b: int | None = Field(
        default=None,
        examples=[""],
        description="Value of the b field",
    )


class ABModelSortOptions(SortOptions):
    a = "a"
    b = "b"


class ABWriter(GenericWriter[ABModel]):
    model = ABModel


class ABReader(GenericReader[ABModel]):
    model = ABModel


class TestGenericWriter:
    def setup_method(self):
        self.ab_writer = ABWriter()
        self.ab_reader = ABReader()

    async def test_add(self, async_session):  # noqa F811
        # Setup
        test_record = ABModel(a=1, b=2)

        # Test
        async with async_session() as session:
            created_object = await self.ab_writer.upsert(
                session=session,
                entity=test_record,
            )
            await session.commit()

        # Validation
        assert created_object is not None
        assert created_object.a == test_record.a
        assert created_object.b == test_record.b

        # Clean-up
        ...

    async def test_get(self, async_session):  # noqa F811
        # Setup
        test_add_record = ABModel(a=1, b=2)

        async with async_session() as session:
            created_object = await self.ab_writer.upsert(
                session=session,
                entity=test_add_record,
            )
            await session.commit()

        # Test
        stored_object = await self.ab_reader.get(
            db=async_session,
            id=created_object.id,
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_object.model_dump()

        # Clean-up
        ...

    async def test_get_by(self, async_session):  # noqa F811
        # Setup
        test_add_record_1 = ABModel(a=1, b=2)
        test_add_record_2 = ABModel(a=2, b=3)

        async with async_session() as session:
            created_object_1 = await self.ab_writer.upsert(
                session=session,
                entity=test_add_record_1,
            )
            _ = await self.ab_writer.upsert(
                session=session,
                entity=test_add_record_2,
            )
            await session.commit()

        # Test
        stored_object = await self.ab_reader.get_by(
            db=async_session,
            filter=ABModelFilter(a=1),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_object_1.model_dump()

        # Clean-up
        ...

    async def test_get_by_with_wrong_filter_params(self, async_session):  # noqa F811
        # Setup
        test_add_record_1 = ABModel(a=1, b=2)
        test_add_record_2 = ABModel(a=2, b=3)

        async with async_session() as session:
            _ = await self.ab_writer.upsert(
                session=session,
                entity=test_add_record_1,
            )
            _ = await self.ab_writer.upsert(
                session=session,
                entity=test_add_record_2,
            )
            await session.commit()

        # Test
        with pytest.raises(CoreException) as exception_info:
            _ = await self.ab_reader.get_by(
                db=async_session,
                filter=ABModelFilter(a=1, b=2),
            )

        # Validation
        assert (
            str(exception_info.value)
            == "Only one filter is allowed for this operation."
        )

        # Clean-up
        ...

    async def test_get_many(self, async_session):  # noqa F811
        # Setup
        page = 1
        items_limit = 5
        a = 1
        b = 1
        test_records = []
        created_objects = []

        for _ in range(10):
            test_record = ABModel(a=a, b=b)
            test_records.append(test_record)

            async with async_session() as session:
                created_object = await self.ab_writer.upsert(
                    session=session,
                    entity=test_record,
                )
                await session.commit()

            created_objects.append(created_object.model_copy(deep=True))
            a += 1

        b = 2
        for _ in range(5):
            test_record = ABModel(a=a, b=b)
            test_records.append(test_record)

            async with async_session() as session:
                created_object = await self.ab_writer.upsert(
                    session=session,
                    entity=test_record,
                )
                await session.commit()

            created_objects.append(created_object.model_copy(deep=True))
            a += 1

        # Test
        stored_objects = await self.ab_reader.get_many(
            db=async_session,
            page=page,
            limit=items_limit,
            filter=ABModelFilter(b=1),
            sort=SortParams(
                sort_by="a",
                sort_order="desc",
            ),
        )

        # Validation
        assert stored_objects is not None
        assert 5 == len(stored_objects)
        for created_object, stored_object in zip(
            reversed(created_objects[5:10]), stored_objects
        ):
            assert stored_object is not None
            assert stored_object.model_dump() == created_object.model_dump()

        # Clean-up
        ...

    async def test_upsert(self, async_session):  # noqa F811
        # Setup
        test_record = ABModel(a=1, b=2)

        async with async_session() as session:
            _ = await self.ab_writer.upsert(
                session=session,
                entity=test_record,
            )
            await session.commit()

        test_update_record = ABModel(a=1, b=2)

        # Test
        async with async_session() as session:
            updated_object = await self.ab_writer.upsert(
                session=session,
                entity=test_update_record,
            )
            await session.commit()

        # Validation
        assert updated_object is not None
        assert updated_object.a == test_update_record.a
        assert updated_object.b == test_update_record.b

        # Clean-up
        ...

    async def test_delete(self, async_session):  # noqa F811
        # Setup
        test_record = ABModel(a=1, b=2)
        async with async_session() as session:
            created_object = await self.ab_writer.upsert(
                session=session,
                entity=test_record,
            )
            await session.commit()

        # Test
        async with async_session() as session:
            deleted_object = await self.ab_writer.delete(
                session=session,
                entity=created_object,
            )
            await session.commit()

        # Validation
        assert deleted_object is not None
        assert deleted_object.a == test_record.a
        assert deleted_object.b == test_record.b
        assert deleted_object.is_active is False
        assert deleted_object.is_deleted is True

        # Clean-up
        ...
