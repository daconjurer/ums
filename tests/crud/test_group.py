import pytest

from uuid import UUID
from datetime import datetime
from ums.crud.group.repository import group_repository
from ums.crud.group.schemas import GroupCreate, GroupUpdate
from ums.middlewares.filter_sort import FilterBy, SortBy, SortOptions
from ums.core.exceptions import InvalidGroupException, InvalidUserException

from ums.db.session import setup_db, drop_db

from tests.fixtures import (
    db,
    initialized_roles,
    initialized_groups,
    initialized_users,
)


def test_add_minimal_group(db, initialized_users):
    # Setup
    test_user_1, test_user_2, _, _ = initialized_users

    setup_db()

    test_add_group = GroupCreate(
        name="Group1",
        location="Glasgow",
        description="Group1 description",
        members_ids=[test_user_1.id, test_user_2.id],
    )

    # Test
    created_group = group_repository.add(db=db, input_object=test_add_group)

    # Validation
    assert created_group is not None
    assert created_group.name == test_add_group.name
    assert created_group.location == test_add_group.location
    assert created_group.members == [test_user_1, test_user_2]
    assert created_group.is_active is True
    assert created_group.is_deleted is False
    assert isinstance(created_group.created_at, datetime)
    assert isinstance(created_group.updated_at, datetime)
    assert created_group.deleted_at is None

    # # Clean-up
    drop_db()


def test_add_group_with_invalid_member(db, initialized_users):
    # Setup
    setup_db()

    test_invalid_member_id = UUID("63aabaf0-5adb-41a8-8aee-e90cafb71042")
    test_add_group = GroupCreate(
        name="Group1",
        location="Glasgow",
        description="Group1 description",
        members_ids=[test_invalid_member_id],
    )

    # Test & validation
    with pytest.raises(InvalidUserException) as exception_info:
        _ = group_repository.add(db=db, input_object=test_add_group)

    assert "Invalid member_id:" in exception_info.value.detail

    # # Clean-up
    drop_db()


def test_get(db, initialized_groups):
    # Setup
    created_group, _, _ = initialized_groups

    setup_db()

    # Test
    stored_object = group_repository.get(db=db, id=created_group.id)

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == created_group.model_dump()

    # Clean-up
    drop_db()


def test_get_by_name(db, initialized_groups):
    # Setup
    created_group, _, _ = initialized_groups
    setup_db()

    # Test
    stored_object = group_repository.get_by(
        db=db,
        filter=FilterBy(key="name", value=created_group.name),
    )

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == created_group.model_dump()

    # Clean-up
    drop_db()


def test_get_by_nonexistent_field(db):
    # Setup
    setup_db()

    # Test
    stored_object = group_repository.get_by(
        db=db,
        filter=FilterBy(key="title", value="Mr"),
    )

    # Validation
    assert stored_object is None

    # Clean-up
    drop_db()


def test_get_many_with_filtering_and_sorting(db, initialized_groups):
    # Setup
    created_group, _, _ = initialized_groups

    setup_db()

    # Test
    stored_objects = group_repository.get_many(
        db=db,
        filter=[
            FilterBy(key="location", value="Glasgow"),
            FilterBy(key="is_active", value="true"),
        ],
        sort=SortBy(key="created_at", by=SortOptions.asc),
    )

    # Validation
    assert stored_objects is not None
    assert 1 == len(stored_objects)
    assert created_group.model_dump() == stored_objects[0].model_dump()

    # Clean-up
    drop_db()


def test_get_many_no_filter(db, initialized_groups):
    # Setup
    created_group_1, created_group_2, created_group_3 = initialized_groups

    setup_db()

    # Test
    stored_objects = group_repository.get_many(db=db)

    # Validation
    assert stored_objects is not None
    assert len(stored_objects) == 3
    assert created_group_1.model_dump() == stored_objects[0].model_dump()
    assert created_group_2.model_dump() == stored_objects[1].model_dump()
    assert created_group_3.model_dump() == stored_objects[2].model_dump()

    # Clean-up
    drop_db()


def test_get_many_with_pagination(db, initialized_groups):
    # Setup
    created_group_1, created_group_2, _ = initialized_groups

    setup_db()

    # Test
    stored_objects = group_repository.get_many(
        db=db,
        page=1,
        limit=2,
    )

    # Validation
    assert stored_objects is not None
    assert len(stored_objects) == 2
    assert created_group_1.model_dump() == stored_objects[0].model_dump()
    assert created_group_2.model_dump() == stored_objects[1].model_dump()

    # Clean-up
    drop_db()


def test_update_valid_group_id(db, initialized_groups, initialized_users):
    # Setup
    test_group, _, _ = initialized_groups
    test_user_1, test_user_2, _, _ = initialized_users
    setup_db()

    test_update_group = GroupUpdate(
        name="Group0",
        location="Skye",
        description="Group0 description",
        members_ids=[test_user_1.id, test_user_2.id],
        is_active=False,
    )

    # Test
    updated_group = group_repository.update(
        db=db,
        obj_id=test_group.id,
        input_object=test_update_group,
    )

    # Validation
    assert updated_group is not None
    assert updated_group.name == test_update_group.name
    assert updated_group.location == test_update_group.location
    assert updated_group.members == [test_user_1, test_user_2]
    assert updated_group.is_active is False
    assert updated_group.is_deleted is False
    assert isinstance(updated_group.created_at, datetime)
    assert isinstance(updated_group.updated_at, datetime)
    assert updated_group.deleted_at is None

    # Clean-up
    drop_db()


def test_update_invalid_group_id(db, initialized_groups, initialized_users):
    # Setup
    test_user_1, _, _, _ = initialized_users
    setup_db()

    test_update_group = GroupUpdate(
        name="Group0",
        location="Skye",
        description="Group0 description",
        members_ids=[test_user_1.id],
        is_active=False,
    )

    # Test & validation
    with pytest.raises(InvalidGroupException) as exception_info:
        _ = group_repository.update(
            db=db,
            obj_id=UUID("66c1aabb-42e9-451e-91bf-f5702b1e6b9f"),
            input_object=test_update_group,
        )

    assert exception_info.value.detail == "Group not found."

    # Clean-up
    drop_db()


def test_delete(db, initialized_groups):
    # Setup
    test_group, _, _ = initialized_groups
    setup_db()

    # Test
    deleted_group = group_repository.delete(db=db, obj_id=test_group.id)

    # Validation
    assert deleted_group is not None
    assert deleted_group.is_active is False
    assert deleted_group.is_deleted is True

    # Clean-up
    drop_db()
