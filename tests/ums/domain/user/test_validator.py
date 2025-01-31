import uuid
from datetime import datetime

import pytest

from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from tests.fixtures.domain import initialized_groups, initialized_roles  # noqa F401
from ums.core import exceptions
from ums.domain.entities import User
from ums.domain.user.schemas import UserCreate, UserUpdate
from ums.domain.user.validator import UserValidator


class TestUserValidator:
    async def test_validate_correct_user(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_roles,  # noqa F811
    ):
        # Setup
        test_group1, test_group2, _ = initialized_groups
        test_role1, _, _ = initialized_roles

        user_create = UserCreate(
            name="TestUser",
            full_name="Test User",
            email="test-user@example.com",
            password="test",
            role_id=test_role1.id,
            group_ids=[test_group1.id, test_group2.id],
        )

        # Test
        user_validator = UserValidator()
        user = await user_validator.validate(async_session, user_create)

        # Validation
        assert isinstance(user, User)
        assert isinstance(user.id, uuid.UUID)
        assert user.name == user_create.name
        assert user.full_name == user_create.full_name
        assert user.email == user_create.email
        assert user.role_id == user_create.role_id
        assert user.groups[0].id == test_group1.id
        assert user.groups[1].id == test_group2.id
        assert user.is_active is True
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.deleted_at is None

    async def test_validate_user_with_invalid_role(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_roles,  # noqa F811
    ):
        # Setup
        invalid_role_id = uuid.uuid4()

        user_create = UserCreate(
            name="TestUser",
            full_name="Test User",
            email="test-user@example.com",
            password="test",
            role_id=invalid_role_id,
        )

        # Test
        user_validator = UserValidator()
        with pytest.raises(exceptions.InvalidRoleException):
            _ = await user_validator.validate(async_session, user_create)

    async def test_validate_user_with_invalid_groups(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_roles,  # noqa F811
    ):
        # Setup
        invalid_group_id = uuid.uuid4()

        user_create = UserCreate(
            name="TestUser",
            full_name="Test User",
            email="test-user@example.com",
            password="test",
            group_ids=[invalid_group_id],
        )

        # Test
        user_validator = UserValidator()
        with pytest.raises(exceptions.InvalidGroupException):
            _ = await user_validator.validate(async_session, user_create)

    async def test_validate_update_user(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_roles,  # noqa F811
    ):
        # Setup
        test_group1, test_group2, _ = initialized_groups
        test_role1, _, _ = initialized_roles

        user_update = UserUpdate(
            id=uuid.uuid4(),
            name="TestUser",
            full_name="Test User",
            email="test-user@example.com",
            password="test",
            group_ids=[test_group1.id, test_group2.id],
            role_id=test_role1.id,
        )

        # Test
        user_validator = UserValidator()
        user = await user_validator.validate(async_session, user_update)

        # Validation
        assert isinstance(user, User)
        assert user.id == user_update.id
        assert user.name == user_update.name
        assert user.full_name == user_update.full_name
        assert user.email == user_update.email
        assert user.role_id == user_update.role_id
        assert user.groups[0].id == test_group1.id
        assert user.groups[1].id == test_group2.id
        assert user.is_active is True
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.deleted_at is None
