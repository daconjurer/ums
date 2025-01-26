from datetime import datetime
from uuid import UUID

import pytest

from tests.original_fixtures import (  # noqa F401
    async_session,
    engine,
    initialized_groups,  # noqa F401
    initialized_roles,  # noqa F401
    initialized_users,  # noqa F401
    setup_and_teardown_db,
)
from ums.core.exceptions import (
    InvalidGroupException,
    InvalidRoleException,
    InvalidUserException,
)
from ums.core.security import verify_password
from ums.crud.base import SortParams
from ums.crud.user.repository import UserFilterParams, user_repository
from ums.crud.user.schemas import UserCreate, UserUpdate


class TestUserRepository:
    def setup_method(self):
        self.test_user_repository = user_repository

    async def test_add_minimal_user(self, async_session):  # noqa F811
        # Setup
        test_add_user = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )

        # Test
        created_user = await user_repository.add(
            db=async_session, input_object=test_add_user
        )

        # Validation
        assert created_user is not None
        assert created_user.name == test_add_user.name
        assert created_user.full_name == test_add_user.full_name
        assert created_user.is_verified is False
        assert created_user.is_active is True
        assert created_user.is_deleted is False
        assert created_user.role_id is None
        assert isinstance(created_user.created_at, datetime)
        assert isinstance(created_user.updated_at, datetime)
        assert verify_password(test_add_user.password, created_user.password)

        # Clean-up
        ...

    async def test_add_user_with_valid_role(
        self,
        async_session,  # noqa F811
        initialized_roles,  # noqa F811
    ):
        # Setup
        test_role, _, _ = initialized_roles

        test_add_user = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
            role_id=test_role.id,
        )

        # Test
        created_user = await user_repository.add(
            db=async_session, input_object=test_add_user
        )

        # Validation
        assert created_user is not None
        assert created_user.name == test_add_user.name
        assert created_user.full_name == test_add_user.full_name
        assert created_user.is_verified is False
        assert created_user.is_active is True
        assert created_user.is_deleted is False
        assert created_user.role_id == str(test_role.id)
        assert isinstance(created_user.created_at, datetime)
        assert isinstance(created_user.updated_at, datetime)
        assert verify_password(test_add_user.password, created_user.password)

        # Clean-up
        ...

    async def test_add_user_with_invalid_role(self, async_session):  # noqa F811
        # Setup
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
            _ = await user_repository.add(db=async_session, input_object=test_add_user)

        assert exception_info.value.detail == "Invalid role_id"

        # Clean-up
        ...

    async def test_add_user_with_valid_groups(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        # Setup
        test_group1, test_group2, _ = initialized_groups

        test_add_user = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
            groups_ids=[test_group1.id, test_group2.id],
        )

        # Test
        created_user = await user_repository.add(
            db=async_session, input_object=test_add_user
        )

        # Validation
        assert created_user is not None
        assert created_user.name == test_add_user.name
        assert created_user.full_name == test_add_user.full_name
        assert created_user.is_verified is False
        assert created_user.is_active is True
        assert created_user.is_deleted is False
        assert created_user.role_id is None
        assert isinstance(created_user.created_at, datetime)
        assert isinstance(created_user.updated_at, datetime)
        assert verify_password(test_add_user.password, created_user.password)

        # Clean-up
        ...

    async def test_add_user_with_invalid_groups(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        # Setup
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
        with pytest.raises(InvalidGroupException):
            _ = await user_repository.add(db=async_session, input_object=test_add_user)

        # Clean-up
        ...

    async def test_get(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        created_user, _, _, _ = initialized_users

        # Test
        stored_object = await user_repository.get(db=async_session, id=created_user.id)

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user.model_dump()

        # Clean-up
        ...

    async def test_get_by_name(self, async_session):  # noqa F811
        # Setup
        test_add_user_1 = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )
        created_user_1 = await user_repository.add(
            db=async_session, input_object=test_add_user_1
        )

        # Test
        stored_object = await user_repository.get_by(
            db=async_session,
            filter=UserFilterParams(name=test_add_user_1.name),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user_1.model_dump()

        # Clean-up
        ...

    async def test_get_by_email(self, async_session):  # noqa F811
        # Setup
        test_add_user_1 = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )
        created_user_1 = await user_repository.add(
            db=async_session, input_object=test_add_user_1
        )

        # Test
        stored_object = await user_repository.get_by(
            db=async_session,
            filter=UserFilterParams(email=test_add_user_1.email),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user_1.model_dump()

        # Clean-up
        ...

    async def test_get_many_with_several_filters(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        created_user, _, _, _ = initialized_users

        # Test
        stored_objects = await user_repository.get_many(
            db=async_session,
            filter=UserFilterParams(
                email="victor.sandoval@rfs-example.com",
                is_active=True,
            ),
        )

        # Validation
        assert stored_objects is not None
        assert 1 == len(stored_objects)
        assert created_user.model_dump() == stored_objects[0].model_dump()

        # Clean-up
        ...

    async def test_get_many_with_sorting(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        expected_full_names = list(user.full_name for user in initialized_users).sort()

        # Test
        stored_objects = await user_repository.get_many(
            db=async_session,
            filter=UserFilterParams(is_active=True),
            sort=SortParams(sort_by="created_at", sort_order="asc"),
        )

        # Validation
        assert stored_objects is not None
        assert len(initialized_users) == len(stored_objects)
        assert (
            expected_full_names
            == list(user.full_name for user in stored_objects).sort()
        )

        # Clean-up
        ...

    async def test_get_many_no_filter(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        (
            created_user_1,
            created_user_2,
            created_user_3,
            created_user_4,
        ) = initialized_users

        # Test
        stored_objects = await user_repository.get_many(db=async_session)

        # Validation
        assert stored_objects is not None
        assert len(stored_objects) == 4
        assert created_user_1.model_dump() == stored_objects[0].model_dump()
        assert created_user_2.model_dump() == stored_objects[1].model_dump()
        assert created_user_3.model_dump() == stored_objects[2].model_dump()
        assert created_user_4.model_dump() == stored_objects[3].model_dump()

        # Clean-up
        ...

    async def test_get_many_with_pagination(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        created_user_1, created_user_2, created_user_3, _ = initialized_users

        # Test
        stored_objects = await user_repository.get_many(
            db=async_session,
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
        ...

    async def test_update_valid_user_id(
        self,
        async_session,  # noqa F811
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_role, _, _ = initialized_roles
        test_group, _, _ = initialized_groups
        test_user, _, _, _ = initialized_users

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
        updated_user = await user_repository.update(
            db=async_session,
            obj_id=test_user.id,
            input_object=test_update_user,
        )

        # Validation
        assert updated_user is not None
        assert updated_user.name == updated_user.name
        assert updated_user.full_name == updated_user.full_name
        assert updated_user.groups[0].model_dump() == test_group.model_dump()
        assert updated_user.role_id == test_update_user.role_id
        assert updated_user.is_verified is True
        assert updated_user.is_active is False
        assert updated_user.is_deleted is False
        assert verify_password(test_update_user.password, updated_user.password)
        assert isinstance(updated_user.created_at, datetime)
        assert isinstance(updated_user.updated_at, datetime)
        assert updated_user.deleted_at is None

        # Clean-up
        ...

    async def test_update_invalid_user_id(
        self,
        async_session,  # noqa F811
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        # Setup
        test_role, _, _ = initialized_roles
        test_group, _, _ = initialized_groups

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
            _ = await user_repository.update(
                db=async_session,
                obj_id=UUID("6e612cad-2406-4695-90a9-a4f143b76c19"),
                input_object=test_update_user,
            )

        assert exception_info.value.detail == "User not found."

        # Clean-up
        ...

    async def test_delete(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user, _, _, _ = initialized_users

        # Test
        deleted_user = await user_repository.delete(
            db=async_session, obj_id=test_user.id
        )

        # Validation
        assert deleted_user is not None
        assert deleted_user.is_active is False
        assert deleted_user.is_deleted is True

        # Clean-up
        ...
