from datetime import datetime
from uuid import UUID

import pytest

from tests.fixtures import (
    db,  # noqa F401
    get_session,
    initialized_groups,  # noqa F401
    initialized_permissions,  # noqa F401
    initialized_roles,  # noqa F401
    initialized_users,  # noqa F401
    setup_and_teardown_db,  # noqa F401
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
        self.test_db = next(get_session())

    def test_add_minimal_user(self):
        # Setup
        test_add_user = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )

        # Test
        created_user = user_repository.add(db=self.test_db, input_object=test_add_user)

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
        ...

    def test_add_user_with_valid_role(self, db, initialized_roles):  # noqa F811
        # Setup
        test_role, _, _ = initialized_roles

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
        created_user = user_repository.add(db=self.test_db, input_object=test_add_user)

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
        ...

    def test_add_user_with_invalid_role(self):
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
            _ = user_repository.add(db=self.test_db, input_object=test_add_user)

        assert exception_info.value.detail == "Invalid role_id"

        # Clean-up
        ...

    def test_add_user_with_valid_groups(self, initialized_groups):  # noqa F811
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
        created_user = user_repository.add(db=self.test_db, input_object=test_add_user)

        # Validation
        assert created_user is not None
        assert created_user.name == test_add_user.name
        assert created_user.full_name == test_add_user.full_name
        assert created_user.groups[0].model_dump() == test_group1.model_dump()
        assert created_user.groups[1].model_dump() == test_group2.model_dump()
        assert created_user.is_verified is False
        assert created_user.is_active is True
        assert created_user.is_deleted is False
        assert created_user.role_id is None
        assert isinstance(created_user.created_at, datetime)
        assert isinstance(created_user.updated_at, datetime)
        assert verify_password(test_add_user.password, created_user.password)

        # Clean-up
        ...

    def test_add_user_with_invalid_groups(self, initialized_groups):  # noqa F811
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
        with pytest.raises(InvalidGroupException) as exception_info:
            _ = user_repository.add(db=self.test_db, input_object=test_add_user)

        assert "Invalid group_id:" in exception_info.value.detail

        # Clean-up
        ...

    def test_get(self):
        # Setup
        test_add_user_1 = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )
        created_user_1 = user_repository.add(
            db=self.test_db, input_object=test_add_user_1
        )

        # Test
        stored_object = user_repository.get(db=self.test_db, id=created_user_1.id)

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user_1.model_dump()

        # Clean-up
        ...

    def test_get_by_name(self):
        # Setup
        test_add_user_1 = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )
        created_user_1 = user_repository.add(
            db=self.test_db, input_object=test_add_user_1
        )

        # Test
        stored_object = user_repository.get_by(
            db=self.test_db,
            filter=UserFilterParams(name=test_add_user_1.name),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user_1.model_dump()

        # Clean-up
        ...

    def test_get_by_email(self):
        # Setup
        test_add_user_1 = UserCreate(
            name="vic",
            full_name="Victor Sandoval",
            email="victor.sandoval@rfs-example.com",
            password="abcdefg",
        )
        created_user_1 = user_repository.add(
            db=self.test_db, input_object=test_add_user_1
        )

        # Test
        stored_object = user_repository.get_by(
            db=self.test_db,
            filter=UserFilterParams(email=test_add_user_1.email),
        )

        # Validation
        assert stored_object is not None
        assert stored_object.model_dump() == created_user_1.model_dump()

        # Clean-up
        ...

    def test_get_many_with_several_filters(self, initialized_users):  # noqa F811
        # Setup
        created_user, _, _, _ = initialized_users

        # Test
        stored_objects = user_repository.get_many(
            db=self.test_db,
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

    def test_get_many_with_sorting(self, initialized_users):  # noqa F811
        # Setup
        expected_full_names = list(user.full_name for user in initialized_users).sort()

        # Test
        stored_objects = user_repository.get_many(
            db=self.test_db,
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

    def test_get_many_no_filter(self, initialized_users):  # noqa F811
        # Setup
        (
            created_user_1,
            created_user_2,
            created_user_3,
            created_user_4,
        ) = initialized_users

        # Test
        stored_objects = user_repository.get_many(db=self.test_db)

        # Validation
        assert stored_objects is not None
        assert len(stored_objects) == 4
        assert created_user_1.model_dump() == stored_objects[0].model_dump()
        assert created_user_2.model_dump() == stored_objects[1].model_dump()
        assert created_user_3.model_dump() == stored_objects[2].model_dump()
        assert created_user_4.model_dump() == stored_objects[3].model_dump()

        # Clean-up
        ...

    def test_get_many_with_pagination(self, initialized_users):  # noqa F811
        # Setup
        created_user_1, created_user_2, created_user_3, _ = initialized_users

        # Test
        stored_objects = user_repository.get_many(
            db=self.test_db,
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

    def test_update_valid_user_id(
        self,
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
        updated_user = user_repository.update(
            db=self.test_db,
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

    def test_update_invalid_user_id(
        self,
        initialized_roles,  # noqa F811
        initialized_groups,  # noqa F811
        initialized_users,  # noqa F811
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
            _ = user_repository.update(
                db=self.test_db,
                obj_id=UUID("6e612cad-2406-4695-90a9-a4f143b76c19"),
                input_object=test_update_user,
            )

        assert exception_info.value.detail == "User not found."

        # Clean-up
        ...

    def test_delete(self, initialized_users):  # noqa F811
        # Setup
        test_user, _, _, _ = initialized_users

        # Test
        deleted_user = user_repository.delete(db=self.test_db, obj_id=test_user.id)

        # Validation
        assert deleted_user is not None
        assert deleted_user.is_active is False
        assert deleted_user.is_deleted is True

        # Clean-up
        ...
