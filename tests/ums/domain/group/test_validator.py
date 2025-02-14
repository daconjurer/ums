import uuid
from datetime import datetime

import pytest

from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from tests.fixtures.domain import (  # noqa F401
    initialized_groups,
    initialized_roles,
    initialized_users,
)
from ums.domain import exceptions
from ums.domain.entities import Group
from ums.domain.group.schemas import GroupCreate, GroupUpdate
from ums.domain.group.validator import GroupValidator


class TestGroupValidator:
    async def test_validate_correct_group(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user1, test_user2, _, _ = initialized_users

        group_create = GroupCreate(
            name="TestGroup",
            location="Test location",
            description="Test description",
            member_ids=[test_user1.id, test_user2.id],
        )

        # Test
        group_validator = GroupValidator()
        group = await group_validator.validate(async_session, group_create)

        # Validation
        assert isinstance(group, Group)
        assert isinstance(group.id, uuid.UUID)
        assert group.name == group_create.name
        assert group.location == group_create.location
        assert group.description == group_create.description
        assert group.members[0].id == test_user1.id
        assert group.members[1].id == test_user2.id
        assert group.is_active is True
        assert group.is_deleted is False
        assert isinstance(group.created_at, datetime)
        assert isinstance(group.updated_at, datetime)
        assert group.deleted_at is None

    async def test_validate_group_with_no_matching_members(
        self,
        async_session,  # noqa F811
    ):
        # Setup
        invalid_user_id = uuid.uuid4()

        group_create = GroupCreate(
            name="TestGroup",
            location="Test location",
            description="Test description",
            member_ids=[invalid_user_id],
        )

        # Test
        group_validator = GroupValidator()
        with pytest.raises(exceptions.InvalidUserException):
            _ = await group_validator.validate(async_session, group_create)

    async def test_validate_group_with_some_invalid_members(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user1, test_user2, _, _ = initialized_users
        invalid_user_id = uuid.uuid4()

        group_create = GroupCreate(
            name="TestGroup",
            location="Test location",
            description="Test description",
            member_ids=[test_user1.id, test_user2.id, invalid_user_id],
        )

        # Test
        group_validator = GroupValidator()
        with pytest.raises(exceptions.InvalidUserException):
            _ = await group_validator.validate(async_session, group_create)

    async def test_validate_update_group(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user1, test_user2, _, _ = initialized_users

        group_update = GroupUpdate(
            id=uuid.uuid4(),
            name="TestGroup",
            location="Test location",
            description="Test description",
            member_ids=[test_user1.id, test_user2.id],
        )

        # Test
        group_validator = GroupValidator()
        group = await group_validator.validate(async_session, group_update)

        # Validation
        assert isinstance(group, Group)
        assert group.id == group_update.id
        assert group.name == group_update.name
        assert group.location == group_update.location
        assert group.description == group_update.description
        assert group.members[0].id == test_user1.id
        assert group.members[1].id == test_user2.id
        assert group.is_active is True
        assert group.is_deleted is False
        assert isinstance(group.created_at, datetime)
        assert isinstance(group.updated_at, datetime)
        assert group.deleted_at is None
