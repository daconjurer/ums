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
from ums.api.exceptions import InvalidGroupException, InvalidUserException
from ums.crud.base import SortParams
from ums.crud.group.repository import GroupFilterParams, group_repository
from ums.crud.group.schemas import GroupCreate, GroupUpdate


class TestGroupRepository:
    def setup_method(self):
        self.test_group_repository = group_repository

    async def test_add_minimal_group(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user_1, test_user_2, _, _ = initialized_users

        test_add_group = GroupCreate(
            name="Group1",
            location="Glasgow",
            description="Group1 description",
            members_ids=[test_user_1.id, test_user_2.id],
        )

        # Test
        created_group = await self.test_group_repository.add(
            db=async_session, input_object=test_add_group
        )

        # Validation
        assert created_group is not None
        assert created_group.name == test_add_group.name
        assert created_group.location == test_add_group.location
        assert created_group.members[0].model_dump() == test_user_1.model_dump()
        assert created_group.members[1].model_dump() == test_user_2.model_dump()
        assert created_group.is_active is True
        assert created_group.is_deleted is False
        assert isinstance(created_group.created_at, datetime)
        assert isinstance(created_group.updated_at, datetime)
        assert created_group.deleted_at is None

        # Clean-up
        ...

    async def test_add_group_with_no_members(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # Setup
        test_user_1, test_user_2, _, _ = initialized_users

        test_add_group = GroupCreate(
            name="Group1",
            location="Glasgow",
            description="Group1 description",
        )

        # Test
        created_group = await self.test_group_repository.add(
            db=async_session, input_object=test_add_group
        )

        # Validation
        assert created_group is not None
        assert created_group.name == test_add_group.name
        assert created_group.location == test_add_group.location
        assert created_group.members == []
        assert created_group.is_active is True
        assert created_group.is_deleted is False
        assert isinstance(created_group.created_at, datetime)
        assert isinstance(created_group.updated_at, datetime)
        assert created_group.deleted_at is None

        # Clean-up
        ...

    async def test_add_group_with_invalid_member(self, async_session):  # noqa F811
        # Setup
        test_invalid_member_id = UUID("63aabaf0-5adb-41a8-8aee-e90cafb71042")
        test_add_group = GroupCreate(
            name="Group1",
            location="Glasgow",
            description="Group1 description",
            members_ids=[test_invalid_member_id],
        )

        # Test & validation
        with pytest.raises(InvalidUserException):
            _ = await self.test_group_repository.add(
                db=async_session, input_object=test_add_group
            )

        # Clean-up
        ...

    async def test_get(self, async_session, initialized_groups):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_object = await self.test_group_repository.get(
            db=async_session, id=created_group.id
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_group.model_dump()

        # Clean-up
        ...

    async def test_get_by_name(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_object = await self.test_group_repository.get_by(
            db=async_session,
            filter=GroupFilterParams(name=created_group.name),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_group.model_dump()

        # Clean-up
        ...

    async def test_get_by_nonexistent_field(self, async_session):  # noqa F811
        # Setup
        ...

        # Test
        stored_object = await self.test_group_repository.get_by(
            db=async_session,
            filter=GroupFilterParams(title="Mr"),
        )

        # Validation
        assert stored_object is None

        # Clean-up
        ...

    async def test_get_many_with_filtering_and_sorting(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_objects = await self.test_group_repository.get_many(
            db=async_session,
            filter=GroupFilterParams(
                location="Glasgow",
                is_active="true",
            ),
            sort=SortParams(sort_by="created_at", sort_order="asc"),
        )

        # Validation
        assert stored_objects is not None
        assert 1 == len(stored_objects)
        assert created_group.model_dump() == stored_objects[0].model_dump()

        # Clean-up
        ...

    async def test_get_many_no_filter(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):  # noqa F811
        # Setup
        created_group_1, created_group_2, created_group_3 = initialized_groups

        # Test
        stored_objects = await self.test_group_repository.get_many(db=async_session)

        # Validation
        assert stored_objects is not None
        assert len(stored_objects) == 3
        assert created_group_1.model_dump() == stored_objects[0].model_dump()
        assert created_group_2.model_dump() == stored_objects[1].model_dump()
        assert created_group_3.model_dump() == stored_objects[2].model_dump()

        # Clean-up
        ...

    async def test_get_many_with_pagination(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
    ):  # noqa F811
        # Setup
        created_group_1, created_group_2, _ = initialized_groups

        # Test
        stored_objects = await self.test_group_repository.get_many(
            db=async_session,
            page=1,
            limit=2,
        )

        # Validation
        assert stored_objects is not None
        assert len(stored_objects) == 2
        assert created_group_1.model_dump() == stored_objects[0].model_dump()
        assert created_group_2.model_dump() == stored_objects[1].model_dump()

        # Clean-up
        ...

    async def test_update_valid_group_id(
        self,
        async_session,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_users,  # noqa F811
    ):  # noqa F811
        # Setup
        test_group, _, _ = initialized_groups
        test_user_1, test_user_2, _, _ = initialized_users

        test_update_group = GroupUpdate(
            name="Group0",
            location="Skye",
            description="Group0 description",
            members_ids=[test_user_1.id, test_user_2.id],
            is_active=False,
        )

        # Test
        updated_group = await self.test_group_repository.update(
            db=async_session,
            obj_id=test_group.id,
            input_object=test_update_group,
        )

        # Validation
        assert updated_group is not None
        assert updated_group.name == test_update_group.name
        assert updated_group.location == test_update_group.location
        assert updated_group.members[0].model_dump() == test_user_1.model_dump()
        assert updated_group.members[1].model_dump() == test_user_2.model_dump()
        assert updated_group.is_active is False
        assert updated_group.is_deleted is False
        assert isinstance(updated_group.created_at, datetime)
        assert isinstance(updated_group.updated_at, datetime)
        assert updated_group.deleted_at is None

        # Clean-up
        ...

    async def test_update_invalid_group_id(
        self,
        async_session,  # noqa F811
        initialized_users,  # noqa F811
    ):  # noqa F811
        # Setup
        test_user_1, _, _, _ = initialized_users

        test_update_group = GroupUpdate(
            name="Group0",
            location="Skye",
            description="Group0 description",
            members_ids=[test_user_1.id],
            is_active=False,
        )

        # Test & validation
        with pytest.raises(InvalidGroupException) as exception_info:
            _ = await self.test_group_repository.update(
                db=async_session,
                obj_id=UUID("66c1aabb-42e9-451e-91bf-f5702b1e6b9f"),
                input_object=test_update_group,
            )

        assert exception_info.value.detail == "Group not found."

        # Clean-up
        ...

    async def test_delete(self, async_session, initialized_groups):  # noqa F811
        # Setup
        test_group, _, _ = initialized_groups

        # Test
        deleted_group = await self.test_group_repository.delete(
            db=async_session, obj_id=test_group.id
        )

        # Validation
        assert deleted_group is not None
        assert deleted_group.is_active is False
        assert deleted_group.is_deleted is True

        # Clean-up
        ...
