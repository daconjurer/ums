import pytest

from uuid import UUID
from datetime import datetime
from ums.crud.group.repository import group_repository
from ums.crud.group.schemas import GroupCreate, GroupUpdate
from ums.middlewares.filter_sort import FilterBy, SortBy, SortOptions
from ums.core.exceptions import InvalidGroupException, InvalidUserException

from tests.fixtures import (
    get_session,
    db,  # noqa F401
    setup_and_teardown_db,  # noqa F401
    initialized_roles,  # noqa F401
    initialized_groups,  # noqa F401
    initialized_users,  # noqa F401
)


class TestGroupRepository:
    def setup_method(self):
        self.test_group_repository = group_repository
        self.test_db = next(get_session())

    def test_add_minimal_group(self, initialized_users):  # noqa F811
        # Setup
        test_user_1, test_user_2, _, _ = initialized_users

        test_add_group = GroupCreate(
            name="Group1",
            location="Glasgow",
            description="Group1 description",
            members_ids=[test_user_1.id, test_user_2.id],
        )

        # Test
        created_group = self.test_group_repository.add(
            db=self.test_db, input_object=test_add_group
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

    def test_add_group_with_invalid_member(self, initialized_users):  # noqa F811
        # Setup
        test_invalid_member_id = UUID("63aabaf0-5adb-41a8-8aee-e90cafb71042")
        test_add_group = GroupCreate(
            name="Group1",
            location="Glasgow",
            description="Group1 description",
            members_ids=[test_invalid_member_id],
        )

        # Test & validation
        with pytest.raises(InvalidUserException) as exception_info:
            _ = self.test_group_repository.add(
                db=self.test_db, input_object=test_add_group
            )

        assert "Invalid member_id:" in exception_info.value.detail

        # # Clean-up
        ...

    def test_get(self, initialized_groups):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_object = self.test_group_repository.get(
            db=self.test_db, id=created_group.id
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_group.model_dump()

        # Clean-up
        ...

    def test_get_by_name(self, initialized_groups):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_object = self.test_group_repository.get_by(
            db=self.test_db,
            filter=FilterBy(key="name", value=created_group.name),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_group.model_dump()

        # Clean-up
        ...

    def test_get_by_nonexistent_field(self):
        # Setup
        ...

        # Test
        stored_object = self.test_group_repository.get_by(
            db=self.test_db,
            filter=FilterBy(key="title", value="Mr"),
        )

        # Validation
        assert stored_object is None

        # Clean-up
        ...

    def test_get_many_with_filtering_and_sorting(self, initialized_groups):  # noqa F811
        # Setup
        created_group, _, _ = initialized_groups

        # Test
        stored_objects = self.test_group_repository.get_many(
            db=self.test_db,
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
        ...

    def test_get_many_no_filter(self, initialized_groups):  # noqa F811
        # Setup
        created_group_1, created_group_2, created_group_3 = initialized_groups

        # Test
        stored_objects = self.test_group_repository.get_many(db=self.test_db)

        # Validation
        assert stored_objects is not None
        assert len(stored_objects) == 3
        assert created_group_1.model_dump() == stored_objects[0].model_dump()
        assert created_group_2.model_dump() == stored_objects[1].model_dump()
        assert created_group_3.model_dump() == stored_objects[2].model_dump()

        # Clean-up
        ...

    def test_get_many_with_pagination(self, initialized_groups):  # noqa F811
        # Setup
        created_group_1, created_group_2, _ = initialized_groups

        # Test
        stored_objects = self.test_group_repository.get_many(
            db=self.test_db,
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

    def test_update_valid_group_id(self, initialized_groups, initialized_users):  # noqa F811
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
        updated_group = self.test_group_repository.update(
            db=self.test_db,
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

    def test_update_invalid_group_id(self, initialized_groups, initialized_users):  # noqa F811
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
            _ = self.test_group_repository.update(
                db=self.test_db,
                obj_id=UUID("66c1aabb-42e9-451e-91bf-f5702b1e6b9f"),
                input_object=test_update_group,
            )

        assert exception_info.value.detail == "Group not found."

        # Clean-up
        ...

    def test_delete(self, initialized_groups):  # noqa F811
        # Setup
        test_group, _, _ = initialized_groups

        # Test
        deleted_group = self.test_group_repository.delete(
            db=self.test_db, obj_id=test_group.id
        )

        # Validation
        assert deleted_group is not None
        assert deleted_group.is_active is False
        assert deleted_group.is_deleted is True

        # Clean-up
        ...
