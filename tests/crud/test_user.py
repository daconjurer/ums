import pytest

from uuid import UUID
from datetime import datetime
from ums.models import Role
from ums.crud.user.repository import user_repository
from ums.crud.user.schemas import UserCreate, UserUpdate
from ums.middlewares.filter_sort import FilterBy, SortBy, SortOptions
from ums.core.security import verify_password
from ums.core.exceptions import (
    InvalidRoleException,
    InvalidGroupException,
    InvalidUserException,
)

from ums.db.session import setup_db, drop_db

from tests.fixtures import (
    db,
    initialized_permissions,
    initialized_roles,
    initialized_groups,
    initialized_users,
)


def test_add_minimal_user(db):
    # Setup
    setup_db()

    test_add_user = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
    )

    # Test
    created_user = user_repository.add(db=db, input_object=test_add_user)

    # Validation
    assert created_user is not None
    assert created_user.name == test_add_user.name
    assert created_user.full_name == test_add_user.full_name
    assert created_user.groups == []
    assert created_user.is_verified is False
    assert created_user.is_active is True
    assert created_user.is_deleted is False
    assert created_user.role_id is None
    assert isinstance(created_user.created_at, datetime)
    assert isinstance(created_user.updated_at, datetime)
    assert verify_password(test_add_user.password, created_user.password)

    # # Clean-up
    drop_db()


def test_add_user_with_valid_role(db, initialized_roles):
    # Setup
    test_role, _, _ = initialized_roles

    setup_db()

    test_add_user = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
        role_id=test_role.id,
    )
    db.add(test_role)
    db.commit()

    # Test
    created_user = user_repository.add(db=db, input_object=test_add_user)

    # Validation
    assert created_user is not None
    assert created_user.name == test_add_user.name
    assert created_user.full_name == test_add_user.full_name
    assert created_user.groups == []
    assert created_user.is_verified is False
    assert created_user.is_active is True
    assert created_user.is_deleted is False
    assert created_user.role_id == test_role.id
    assert isinstance(created_user.created_at, datetime)
    assert isinstance(created_user.updated_at, datetime)
    assert verify_password(test_add_user.password, created_user.password)

    # Clean-up
    drop_db()


def test_add_user_with_invalid_role(db):
    # Setup
    setup_db()

    invalid_role_id = UUID("5f0f6db0-f89f-4323-83bb-956767ad0a17")
    test_add_user = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
        role_id=invalid_role_id,
    )

    # Test & validation
    with pytest.raises(InvalidRoleException) as exception_info:
        _ = user_repository.add(db=db, input_object=test_add_user)

    assert exception_info.value.detail == "Invalid role_id"

    # Clean-up
    drop_db()


def test_add_user_with_valid_groups(db, initialized_groups):
    # Setup
    test_group1, test_group2, _ = initialized_groups
    setup_db()

    test_add_user = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
        groups_ids=[test_group1.id, test_group2.id],
    )

    # Test
    created_user = user_repository.add(db=db, input_object=test_add_user)

    # Validation
    assert created_user is not None
    assert created_user.name == test_add_user.name
    assert created_user.full_name == test_add_user.full_name
    assert created_user.groups == [test_group1, test_group2]
    assert created_user.is_verified is False
    assert created_user.is_active is True
    assert created_user.is_deleted is False
    assert created_user.role_id is None
    assert isinstance(created_user.created_at, datetime)
    assert isinstance(created_user.updated_at, datetime)
    assert verify_password(test_add_user.password, created_user.password)

    # Clean-up
    drop_db()


def test_add_user_with_invalid_groups(db, initialized_groups):
    # Setup
    setup_db()

    test_invalid_group_id_1 = UUID("ddd7f04f-cdc6-4844-a51a-0999c51cf2fa")
    test_invalid_group_id_2 = UUID("9502e2e9-9485-4321-936d-6b01ebaecd36")
    test_add_user = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
        groups_ids=[test_invalid_group_id_1, test_invalid_group_id_2],
    )

    # Test & validation
    with pytest.raises(InvalidGroupException) as exception_info:
        _ = user_repository.add(db=db, input_object=test_add_user)

    assert "Invalid group_id:" in exception_info.value.detail

    # Clean-up
    drop_db()


def test_get(db):
    # Setup
    setup_db()

    test_add_user_1 = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
    )
    created_user_1 = user_repository.add(db=db, input_object=test_add_user_1)

    # Test
    stored_object = user_repository.get(db=db, id=created_user_1.id)

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == created_user_1.model_dump()

    # Clean-up
    drop_db()


def test_get_by_name(db):
    # Setup
    setup_db()

    test_add_user_1 = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
    )
    created_user_1 = user_repository.add(db=db, input_object=test_add_user_1)

    # Test
    stored_object = user_repository.get_by(
        db=db,
        filter=FilterBy(key="name", value=test_add_user_1.name),
    )

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == created_user_1.model_dump()

    # Clean-up
    drop_db()


def test_get_by_email(db):
    # Setup
    setup_db()

    test_add_user_1 = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
    )
    created_user_1 = user_repository.add(db=db, input_object=test_add_user_1)

    # Test
    stored_object = user_repository.get_by(
        db=db,
        filter=FilterBy(key="email", value=test_add_user_1.email),
    )

    # Validation
    assert stored_object is not None
    assert stored_object.model_dump() == created_user_1.model_dump()

    # Clean-up
    drop_db()


def test_get_by_nonexistent_field(db):
    # Setup
    setup_db()

    test_add_user_1 = UserCreate(
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password="abcdefg",
    )
    _ = user_repository.add(db=db, input_object=test_add_user_1)

    # Test
    stored_object = user_repository.get_by(
        db=db,
        filter=FilterBy(key="title", value="Mr"),
    )

    # Validation
    assert stored_object is None

    # Clean-up
    drop_db()


def test_get_many_with_filtering_and_sorting(db, initialized_users):
    # Setup
    created_user, _, _, _ = initialized_users

    setup_db()

    # Test
    stored_objects = user_repository.get_many(
        db=db,
        filter=[
            FilterBy(key="email", value="victor.sandoval@rfs-example.com"),
            FilterBy(key="is_active", value="true"),
        ],
        sort=SortBy(key="created_at", by=SortOptions.asc),
    )

    # Validation
    assert stored_objects is not None
    assert 1 == len(stored_objects)
    assert created_user.model_dump() == stored_objects[0].model_dump()

    # Clean-up
    drop_db()


def test_get_many_no_filter(db, initialized_users):
    # Setup
    created_user_1, created_user_2, created_user_3, created_user_4 = initialized_users

    setup_db()

    # Test
    stored_objects = user_repository.get_many(db=db)

    # Validation
    assert stored_objects is not None
    assert len(stored_objects) == 4
    assert created_user_1.model_dump() == stored_objects[0].model_dump()
    assert created_user_2.model_dump() == stored_objects[1].model_dump()
    assert created_user_3.model_dump() == stored_objects[2].model_dump()
    assert created_user_4.model_dump() == stored_objects[3].model_dump()

    # Clean-up
    drop_db()


def test_get_many_with_pagination(db, initialized_users):
    # Setup
    created_user_1, created_user_2, created_user_3, _ = initialized_users

    setup_db()

    # Test
    stored_objects = user_repository.get_many(
        db=db,
        page=1,
        limit=3,
    )

    # Validation
    assert stored_objects is not None
    assert len(stored_objects) == 3
    assert created_user_1.model_dump() == stored_objects[0].model_dump()
    assert created_user_2.model_dump() == stored_objects[1].model_dump()
    assert created_user_3.model_dump() == stored_objects[2].model_dump()

    # Clean-up
    drop_db()


def test_update_valid_user_id(
    db, initialized_roles, initialized_groups, initialized_users
):
    # Setup
    test_role, _, _ = initialized_roles
    test_group, _, _ = initialized_groups
    test_user, _, _, _ = initialized_users
    setup_db()

    test_update_user = UserUpdate(
        name="vic1",
        full_name="Victor Sandoval",
        email="victor.sandoval.1@rfs-example.com",
        password="password1",
        role_id=test_role.id,
        groups_ids=[test_group.id],
        is_active=False,
        is_verified=True,
    )

    # Test
    updated_user = user_repository.update(
        db=db,
        obj_id=test_user.id,
        input_object=test_update_user,
    )

    # Validation
    assert updated_user is not None
    assert updated_user.name == updated_user.name
    assert updated_user.full_name == updated_user.full_name
    assert updated_user.groups == [test_group]
    assert updated_user.role_id == test_update_user.role_id
    assert updated_user.is_verified is True
    assert updated_user.is_active is False
    assert updated_user.is_deleted is False
    assert verify_password(test_update_user.password, updated_user.password)
    assert isinstance(updated_user.created_at, datetime)
    assert isinstance(updated_user.updated_at, datetime)
    assert updated_user.deleted_at is None

    # Clean-up
    drop_db()


def test_update_invalid_user_id(
    db, initialized_roles, initialized_groups, initialized_users
):
    # Setup
    test_role, _, _ = initialized_roles
    test_group, _, _ = initialized_groups
    setup_db()

    test_update_user = UserUpdate(
        name="vic1",
        full_name="Victor Sandoval",
        email="victor.sandoval.1@rfs-example.com",
        password="password1",
        role_id=test_role.id,
        groups_ids=[test_group.id],
        is_active=False,
        is_verified=True,
    )

    # Test & validation
    with pytest.raises(InvalidUserException) as exception_info:
        _ = user_repository.update(
            db=db,
            obj_id=UUID("6e612cad-2406-4695-90a9-a4f143b76c19"),
            input_object=test_update_user,
        )

    assert exception_info.value.detail == "User not found."

    # Clean-up
    drop_db()


def test_delete(db, initialized_users):
    # Setup
    test_user, _, _, _ = initialized_users
    setup_db()

    # Test
    deleted_user = user_repository.delete(db=db, obj_id=test_user.id)

    # Validation
    assert deleted_user is not None
    assert deleted_user.is_active is False
    assert deleted_user.is_deleted is True

    # Clean-up
    drop_db()
