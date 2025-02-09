from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from tests.fixtures.domain import initialized_roles  # noqa F401
from ums.domain.permissions.schemas import PermissionsCreate
from ums.domain.permissions.service import PermissionsService


class TestPermissionsService:
    async def test_add_permissions(
        self,
    ):
        permissions_service = PermissionsService()
        permissions = await permissions_service.add_permissions(
            PermissionsCreate(
                name="test_permissions",
                description="test_description",
            )
        )

        assert permissions is not None
        assert permissions.id is not None
        assert permissions.name == "test_permissions"
        assert permissions.description == "test_description"

    async def test_get_by_role_id(
        self,
        initialized_roles,  # noqa F811
    ):
        test_role1, test_role2, _ = initialized_roles

        permissions_service = PermissionsService()
        permissions = await permissions_service.get_by_role_id(test_role1.id)

        assert len(permissions) == 2
        assert permissions[0].id == test_role1.permissions[0].id
        assert permissions[1].id == test_role1.permissions[1].id
