from datetime import datetime
from uuid import UUID, uuid4

import pytest

from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from tests.fixtures.domain import (
    initialized_groups,  # noqa F811
    initialized_roles,  # noqa F811
    initialized_user_with_role_and_groups,  # noqa F811
    initialized_users,  # noqa F811
)
from ums.core.utils.filter_sort import SortParams
from ums.core.utils.security import verify_password
from ums.domain import exceptions
from ums.domain.entities import User
from ums.domain.user.schemas import UserCreate, UserUpdate
from ums.domain.user.service import UserFilterParams, UserService


class TestUserService:
    async def test_add_valid_user(
        self,
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        test_role1, _, _ = initialized_roles
        test_group1, _, _ = initialized_groups

        user_create = UserCreate(
            name="test_user",
            full_name="Test User",
            email="test.user@rfs-example.com",
            password="password123",
            role_id=test_role1.id,
            group_ids=[test_group1.id],
        )

        user_service = UserService()
        user = await user_service.add_user(user_create)

        assert user is not None
        assert isinstance(user, User)
        assert isinstance(user.id, UUID)
        assert user.name == user_create.name
        assert user.full_name == user_create.full_name
        assert user.email == user_create.email
        assert verify_password(user_create.password, user.password)

    async def test_add_user_with_invalid_role(
        self,
    ):
        user_create = UserCreate(
            name="test_user",
            full_name="Test User",
            email="test.user@rfs-example.com",
            password="password123",
            role_id=uuid4(),
        )

        user_service = UserService()

        with pytest.raises(exceptions.InvalidRoleException):
            _ = await user_service.add_user(user_create)

    async def test_add_user_with_invalid_group(
        self,
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        test_role1, _, _ = initialized_roles

        user_create = UserCreate(
            name="test_user",
            full_name="Test User",
            email="test.user@rfs-example.com",
            password="password123",
            role_id=test_role1.id,
            group_ids=[uuid4()],
        )

        user_service = UserService()

        with pytest.raises(exceptions.InvalidGroupException):
            _ = await user_service.add_user(user_create)

    async def test_add_user_when_no_active_groups(
        self,
        initialized_roles,  # noqa F811
    ):
        test_role1, _, _ = initialized_roles

        user_create = UserCreate(
            name="test_user",
            full_name="Test User",
            email="test.user@rfs-example.com",
            password="password123",
            role_id=test_role1.id,
            group_ids=[uuid4()],
        )

        user_service = UserService()

        with pytest.raises(exceptions.InvalidGroupException):
            _ = await user_service.add_user(user_create)

    async def test_update_user_successfully(
        self,
        initialized_users,  # noqa F811
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
    ):
        test_user1, _, _, _ = initialized_users
        test_role1, _, _ = initialized_roles
        test_group1, _, _ = initialized_groups

        user_update = UserUpdate(
            id=test_user1.id,
            name="EL",
            full_name="Esteban Luna",
            email="esteban.luna@rfs-example.com",
            password="password123",
            role_id=test_role1.id,
            group_ids=[test_group1.id],
        )

        user_service = UserService()
        user = await user_service.update_user(user_update)

        assert user is not None
        assert isinstance(user, User)
        assert user.name == user_update.name
        assert user.full_name == user_update.full_name
        assert user.email == user_update.email
        assert verify_password(user_update.password, user.password)
        assert user.role_id == user_update.role_id
        assert user.groups[0].id == user_update.group_ids[0]

    async def test_update_user_when_user_does_not_exist(
        self,
    ):
        user_update = UserUpdate(
            id=uuid4(),
            name="test_user",
        )

        user_service = UserService()

        with pytest.raises(exceptions.InvalidUserException):
            _ = await user_service.update_user(user_update)

    async def test_update_user_verification_timestamp(
        self,
        initialized_users,  # noqa F811
    ):
        test_user1, _, _, _ = initialized_users

        user_update = UserUpdate(
            id=test_user1.id,
            is_verified=True,
        )

        user_service = UserService()
        user = await user_service.update_user(user_update)

        assert user is not None
        assert isinstance(user, User)
        assert user.is_verified
        assert user.verified_at is not None
        assert isinstance(user.verified_at, datetime)

    async def test_get_user_by_name(
        self,
        initialized_users,  # noqa F811
    ):
        test_user1, _, _, _ = initialized_users

        user_service = UserService()
        user = await user_service.get_user_by_name(test_user1.name)

        assert user is not None
        assert isinstance(user, User)
        assert user.name == test_user1.name

    async def test_get_user_role_id(
        self,
        initialized_user_with_role_and_groups,  # noqa F811
    ):
        test_user1 = initialized_user_with_role_and_groups

        user_service = UserService()
        role_id = await user_service.get_user_role_id(test_user1.name)

        assert role_id is not None
        assert isinstance(role_id, UUID)
        assert role_id == test_user1.role_id

    async def test_get_user_role_id_when_user_does_not_exist(
        self,
    ):
        user_service = UserService()
        role_id = await user_service.get_user_role_id("nonexistent_user")

        assert role_id is None

    async def test_get_user_groups_order_by_full_name(
        self,
        initialized_users,  # noqa F811
    ):
        test_user1, _, _, _ = initialized_users

        user_service = UserService()
        users = await user_service.get_users(
            filter=UserFilterParams(is_active=True),
            sort=SortParams(sort_by="full_name", sort_order="asc"),
            limit=4,
            page=1,
        )

        assert users is not None
        assert len(users) == 4
        assert users[0].full_name == "Juan Valdez"
        assert users[1].full_name == "Lupe Pintos"
        assert users[2].full_name == "Sebastian Manzano"
        assert users[3].full_name == "Victor Sandoval"
