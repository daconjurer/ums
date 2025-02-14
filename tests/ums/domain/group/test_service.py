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
from ums.domain import exceptions
from ums.domain.entities import Group
from ums.domain.group.schemas import GroupCreate, GroupUpdate
from ums.domain.group.service import GroupFilterParams, GroupService


class TestGroupService:
    async def test_add_valid_group(
        self,
        initialized_users,  # noqa F811
    ):
        test_user1, _, _, _ = initialized_users

        group_create = GroupCreate(
            name="test_group",
            location="test_location",
            description="test_description",
            member_ids=[test_user1.id],
        )

        group_service = GroupService()
        group = await group_service.add_group(group_create)

        assert group is not None
        assert isinstance(group, Group)
        assert isinstance(group.id, UUID)
        assert group.name == group_create.name
        assert group.location == group_create.location
        assert group.description == group_create.description
        assert group.members[0].id == test_user1.id

    async def test_add_group_with_invalid_member(
        self,
        initialized_users,  # noqa F811
    ):
        group_create = GroupCreate(
            name="test_group",
            location="test_location",
            description="test_description",
            member_ids=[uuid4()],
        )

        group_service = GroupService()

        with pytest.raises(exceptions.InvalidUserException):
            _ = await group_service.add_group(group_create)

    async def test_add_group_when_no_active_members(
        self,
    ):
        group_create = GroupCreate(
            name="test_group",
            location="test_location",
            description="test_description",
            member_ids=[uuid4()],
        )

        group_service = GroupService()

        with pytest.raises(exceptions.InvalidUserException):
            _ = await group_service.add_group(group_create)

    async def test_update_group_successfully(
        self,
        initialized_groups,  # noqa F811
    ):
        test_group1, _, _ = initialized_groups

        group_update = GroupUpdate(
            id=test_group1.id,
            name="test_group",
            location="test_location",
            description="test_description",
        )

        group_service = GroupService()
        group = await group_service.update_group(group_update)

        assert group is not None
        assert isinstance(group, Group)
        assert group.name == group_update.name
        assert group.location == group_update.location
        assert group.description == group_update.description

    async def test_update_group_when_group_does_not_exist(
        self,
    ):
        group_update = GroupUpdate(
            id=uuid4(),
            name="test_group",
        )

        group_service = GroupService()

        with pytest.raises(exceptions.InvalidGroupException):
            _ = await group_service.update_group(group_update)

    async def test_get_group_by_name(
        self,
        initialized_groups,  # noqa F811
    ):
        test_group1, _, _ = initialized_groups

        group_service = GroupService()
        group = await group_service.get_group_by_name(test_group1.name)

        assert group is not None
        assert isinstance(group, Group)
        assert group.name == test_group1.name

    async def test_get_group_by_location(
        self,
        initialized_groups,  # noqa F811
    ):
        test_group1, _, _ = initialized_groups

        group_service = GroupService()
        group = await group_service.get_group_by_location(test_group1.location)

        assert group is not None
        assert isinstance(group, Group)
        assert group.location == test_group1.location

    async def test_get_groups_order_by_location(
        self,
        initialized_groups,  # noqa F811
    ):
        test_group1, _, _ = initialized_groups

        group_service = GroupService()
        groups = await group_service.get_groups(
            filter=GroupFilterParams(is_active=True),
            sort=SortParams(sort_by="location", sort_order="asc"),
            limit=4,
            page=1,
        )

        assert groups is not None
        assert len(groups) == 3
        assert groups[0].location == "Edinburgh"
        assert groups[1].location == "Glasgow"
        assert groups[2].location == "Inverness"

    # async def test_get_user_by_name(
    #     self,
    #     initialized_users,  # noqa F811
    # ):
    #     test_user1, _, _, _ = initialized_users

    #     user_service = GroupService()
    #     user = await user_service.get_user_by_name(test_user1.name)

    #     assert user is not None
    #     assert isinstance(user, Group)
    #     assert user.name == test_user1.name

    # async def test_get_user_role_id(
    #     self,
    #     initialized_user_with_role_and_groups,  # noqa F811
    # ):
    #     test_user1 = initialized_user_with_role_and_groups

    #     user_service = GroupService()
    #     role_id = await user_service.get_user_role_id(test_user1.name)

    #     assert role_id is not None
    #     assert isinstance(role_id, UUID)
    #     assert role_id == test_user1.role_id

    # async def test_get_user_role_id_when_user_does_not_exist(
    #     self,
    # ):
    #     user_service = GroupService()
    #     role_id = await user_service.get_user_role_id("nonexistent_user")

    #     assert role_id is None
