import pytest

import uuid
from sqlmodel import Field

from ums.crud.base import BaseRepository, UpdateSchema, CreateSchema
from ums.models import Base
from ums.db.session import get_session, setup_db, drop_db
from ums.core.exceptions import UMSException


@pytest.fixture
def db():
    return next(get_session())


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


def test_add(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    test_add_record = DummyModelCreate(a=1, b=2)

    # Test
    created_object = crud_repository.add(db=db, input_object=test_add_record)

    # Validation
    assert created_object is not None
    assert created_object.a == test_add_record.a
    assert created_object.b == test_add_record.b

    # Clean-up
    drop_db()


def test_get(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    test_record = DummyModel(a=1, b=2)
    created_object = crud_repository.add(db=db, input_object=test_record)

    # Test
    stored_object = crud_repository.get(db=db, id=created_object.id)

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == test_record.model_dump()

    # Clean-up
    drop_db()


def test_get_many(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    page = 2
    items_limit = 10
    x = 1
    y = 10
    test_records = []

    for _ in range(15):
        test_record = DummyModel(a=x, b=y)
        test_records.append(test_record)
        crud_repository.add(db=db, input_object=test_record)
        x += 1
        y += 1

    # Test
    stored_objects = crud_repository.get_many(
        db=db,
        page=page,
        limit=items_limit,
    )

    # Validation
    assert stored_objects is not None
    assert 5 == len(stored_objects)
    for test_record, stored_object in zip(test_records[-5:], stored_objects):
        assert stored_object.model_dump() == test_record.model_dump()

    # Clean-up
    drop_db()


def test_update_valid(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    test_record = DummyModel(a=1, b=2)
    created_object = crud_repository.add(db=db, input_object=test_record)
    test_update_record = DummyModelCreate(a=1, b=2)

    # Test
    updated_object = crud_repository.update(
        db=db,
        obj_id=created_object.id,
        input_object=test_record,
    )

    # Validation
    assert updated_object is not None
    assert updated_object.a == test_update_record.a
    assert updated_object.b == test_update_record.b

    # Clean-up
    drop_db()


def test_update_invalid(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    test_record = DummyModel(a=1, b=2)
    _ = crud_repository.add(db=db, input_object=test_record)

    # Test & validation
    with pytest.raises(UMSException) as exception_info:
        _ = crud_repository.update(
            db=db,
            obj_id=uuid.UUID("293f88c2-e19c-4e9d-b133-277d4e76a479"),
            input_object=test_record,
        )

    assert exception_info.value.detail == "Object not found."

    # Clean-up
    drop_db()


def test_delete(db):
    # Setup
    setup_db()

    crud_repository = BaseRepository(model=DummyModel)
    test_record = DummyModel(a=1, b=2)
    created_object = crud_repository.add(db=db, input_object=test_record)

    # Test
    deleted_object = crud_repository.delete(db=db, obj_id=created_object.id)

    # Validation
    assert deleted_object is not None
    assert deleted_object.a == test_record.a
    assert deleted_object.b == test_record.b

    # Clean-up
    drop_db()
