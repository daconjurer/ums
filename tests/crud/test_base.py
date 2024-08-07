import uuid

import pytest
from sqlmodel import Field

from tests.fixtures import get_session, setup_and_teardown_db  # noqa F401
from ums.core.exceptions import UMSException
from ums.crud.base import BaseRepository, CreateSchema, UpdateSchema
from ums.models import Base


class DummyModel(Base, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    a: int
    b: int
    is_active: bool = True
    is_deleted: bool = False


class DummyModelCreate(CreateSchema):
    a: int
    b: int


class DummyModelUpdate(UpdateSchema):
    a: int
    b: int


class TestBaseRepository:
    def setup_method(self):
        self.test_crud_repository = BaseRepository(model=DummyModel)
        self.test_db = next(get_session())

    def test_class_add(self):
        # Setup
        test_add_record = DummyModelCreate(a=1, b=2)

        # Test
        created_object = self.test_crud_repository.add(
            db=self.test_db,
            input_object=test_add_record,
        )

        # Validation
        assert created_object is not None
        assert created_object.a == test_add_record.a
        assert created_object.b == test_add_record.b

        # Clean-up
        ...

    def test_get(self):
        # Setup
        test_record = DummyModel(a=1, b=2)
        created_object = self.test_crud_repository.add(
            db=self.test_db,
            input_object=test_record,
        )

        # Test
        stored_object = self.test_crud_repository.get(
            db=self.test_db,
            id=created_object.id,
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_object.model_dump()

        # Clean-up
        ...

    def test_get_many(self):
        # Setup
        page = 2
        items_limit = 10
        x = 1
        y = 10
        test_records = []
        created_objects = []

        for _ in range(15):
            test_record = DummyModel(a=x, b=y)
            test_records.append(test_record)

            created_object = self.test_crud_repository.add(
                db=self.test_db,
                input_object=test_record,
            )
            created_objects.append(created_object.model_copy(deep=True))
            x += 1
            y += 1

        # Test
        stored_objects = self.test_crud_repository.get_many(
            db=self.test_db,
            page=page,
            limit=items_limit,
        )

        # Validation
        assert stored_objects is not None
        assert 5 == len(stored_objects)
        for created_object, stored_object in zip(created_objects[-5:], stored_objects):
            assert stored_object is not None
            assert stored_object.model_dump() == created_object.model_dump()

        # Clean-up
        ...

    def test_update_valid(self):
        # Setup
        test_record = DummyModel(a=1, b=2)
        created_object = self.test_crud_repository.add(
            db=self.test_db,
            input_object=test_record,
        )
        test_update_record = DummyModelCreate(a=1, b=2)

        # Test
        updated_object = self.test_crud_repository.update(
            db=self.test_db,
            obj_id=created_object.id,
            input_object=test_record,
        )

        # Validation
        assert updated_object is not None
        assert updated_object.a == test_update_record.a
        assert updated_object.b == test_update_record.b

        # Clean-up
        ...

    def test_update_invalid(self):
        # Setup
        test_record = DummyModel(a=1, b=2)
        _ = self.test_crud_repository.add(
            db=self.test_db,
            input_object=test_record,
        )

        # Test & validation
        with pytest.raises(UMSException) as exception_info:
            _ = self.test_crud_repository.update(
                db=self.test_db,
                obj_id=uuid.UUID("293f88c2-e19c-4e9d-b133-277d4e76a479"),
                input_object=test_record,
            )

        assert exception_info.value.detail == "Object not found."

        # Clean-up
        ...

    def test_delete(self):
        # Setup
        test_record = DummyModel(a=1, b=2)
        created_object = self.test_crud_repository.add(
            db=self.test_db,
            input_object=test_record,
        )

        # Test
        deleted_object = self.test_crud_repository.delete(
            db=self.test_db,
            obj_id=created_object.id,
        )

        # Validation
        assert deleted_object is not None
        assert deleted_object.a == test_record.a
        assert deleted_object.b == test_record.b

        # Clean-up
        ...
