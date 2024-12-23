from uuid import UUID

import pytest_asyncio
from fastapi.testclient import TestClient

from ums.core.app_factory import create_app
from ums.core.security import get_password_hash
from ums.db.async_connection import (
    DatabaseManager,
    create_custom_engine,
    get_async_session,
)
from ums.models import Group, Permissions, Role, User
from ums.settings.application import get_app_settings

db_settings = get_app_settings().db


@pytest_asyncio.fixture(scope="class")
async def async_session(session_generator=get_async_session):
    return session_generator


@pytest_asyncio.fixture(scope="class")
async def engine():
    engine = create_custom_engine(str(db_settings.uri))
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown_db(engine):
    await DatabaseManager.drop_db(engine=engine)
    await DatabaseManager.setup_db(engine=engine)
    yield
    await DatabaseManager.drop_db(engine=engine)


@pytest_asyncio.fixture
async def initialized_roles(async_session):  # noqa F811
    users_permission = Permissions(
        id=UUID("c0d6a4f1-bb1d-471f-ac5f-06c2691c0390"),
        name="users",
        description="List all the users",
    )
    me_permission = Permissions(
        id=UUID("797bf248-6b79-4218-98db-190502497c59"),
        name="me",
        description="List all the user's details",
    )

    admin_role = Role(
        id=UUID("30ba096f-1d1a-4d6e-bd35-0d2c83a6dc7b"),
        name="Admin",
        description="Admin role description",
        permissions=[users_permission, me_permission],
    )
    maintainer_role = Role(
        id=UUID("7995971c-a9a7-4737-a440-cf0bf2ae353c"),
        name="Maintainer",
        description="Maintainer role description",
        permissions=[me_permission],
    )
    user_role = Role(
        id=UUID("67276d92-b3d8-40c6-b5b6-327add57796a"),
        name="User",
        description="User role description",
    )

    async with async_session() as session:
        session.add_all([users_permission, me_permission])
        session.add_all([admin_role, maintainer_role, user_role])
        admin_role = await session.merge(admin_role)
        maintainer_role = await session.merge(maintainer_role)
        user_role = await session.merge(user_role)

    yield admin_role, maintainer_role, user_role


@pytest_asyncio.fixture
async def initialized_groups(async_session):
    test_group_1 = Group(
        id=UUID("369eb0b1-50c5-4296-b245-56e7c2a6fa57"),
        name="Group1",
        location="Glasgow",
    )
    test_group_2 = Group(
        id=UUID("9396819d-a724-4555-a204-72b2408dbfd0"),
        name="Group2",
        location="Edinburgh",
    )
    test_group_3 = Group(
        id=UUID("1dac92b4-e315-4af1-ac2c-21daf08e5eba"),
        name="Group3",
        location="Inverness",
    )

    async with async_session() as session:
        session.add_all([test_group_1, test_group_2, test_group_3])
        test_group_1

    yield test_group_1, test_group_2, test_group_3


@pytest_asyncio.fixture
async def initialized_users(async_session):
    test_user_1 = User(
        id=UUID("f18941a4-bb0e-444a-b6a0-a19509cc6089"),
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password=get_password_hash("password1"),
    )
    test_user_2 = User(
        id=UUID("9d7a39d8-4e25-4368-8bc9-8e795ffb9e04"),
        name="sebito",
        full_name="Sebastian Manzano",
        email="sebastian.manzano@rfs-example.com",
        password=get_password_hash("password2"),
    )
    test_user_3 = User(
        id=UUID("17187ad4-90e5-4987-af91-60e70c925761"),
        name="LuPintos",
        full_name="Lupe Pintos",
        email="lupe.pintos@rfs-example.com",
        password=get_password_hash("password3"),
    )
    test_user_4 = User(
        id=UUID("2fe19756-b3dd-4ca4-9ea9-69852b15c255"),
        name="JohnyVals",
        full_name="Juan Valdez",
        email="juan.valdez@rfs-example.com",
        password=get_password_hash("password4"),
    )

    async with async_session() as session:
        session.add_all([test_user_1, test_user_2, test_user_3, test_user_4])
        test_user_1 = await session.merge(test_user_1)
        test_user_2 = await session.merge(test_user_2)
        test_user_3 = await session.merge(test_user_3)
        test_user_4 = await session.merge(test_user_4)

    yield test_user_1, test_user_2, test_user_3, test_user_4


@pytest_asyncio.fixture
async def initialized_admin(async_session):
    users_permission = Permissions(
        id=UUID("90d7a1fc-c255-4315-a89d-67e3c7b09ae1"),
        name="users",
        description="List all the users",
    )
    me_permission = Permissions(
        id=UUID("54f5244e-fc40-4f80-b7bc-b342522b89ac"),
        name="me",
        description="List all the user's details",
    )
    admin_role = Role(
        id=UUID("8750dc45-b226-4f9c-8707-a1fadba0efaf"),
        name="Admin",
        description="Admin role description",
        permissions=[users_permission, me_permission],
    )

    admin_group = Group(
        id=UUID("343887c7-7f49-46e6-8a0a-5f7ed66576cb"),
        name="AdminGroup",
        location="Glasgow",
    )

    admin_user = User(
        id=UUID("6dd0434c-ca7f-4454-8bb8-d589b8a0ce99"),
        name="TheAdmin",
        full_name="The Admin",
        email="the.admin@rfs-example.com",
        password=get_password_hash("adminspassword1"),
        groups=[admin_group],
        role_id=admin_role.id,
    )

    async with async_session() as session:
        session.add(users_permission)
        session.add(me_permission)

        session.add(admin_role)
        session.add(admin_group)

        session.add(admin_user)

        admin_user = await session.merge(admin_user)
        admin_role = await session.merge(admin_role)

    yield admin_user, admin_role


@pytest_asyncio.fixture
async def initialized_maintainer(async_session):
    me_permission = Permissions(
        id=UUID("59899a9a-5244-40b6-89d8-2758cac197b8"),
        name="me",
        description="List all the user's details",
    )

    maintainer_role = Role(
        id=UUID("93d72368-ece7-433a-b5f1-243466f9db30"),
        name="Maintainer",
        description="Maintainer role description",
        permissions=[me_permission],
    )

    maintainer_group = Group(
        id=UUID("196acb0e-5133-4b0a-8b71-839d0b03605c"),
        name="MaintainerGroup",
        location="Glasgow",
    )

    maintainer_user = User(
        id=UUID("ea1a76c1-3a1e-4952-a190-d510843b36a7"),
        name="TheMaintainer",
        full_name="The Maintainer",
        email="the.maintainer@rfs-example.com",
        password=get_password_hash("maintainerspassword1"),
        groups=[maintainer_group],
        role_id=maintainer_role.id,
    )

    async with async_session() as session:
        session.add(me_permission)

        session.add(maintainer_role)
        session.add(maintainer_group)

        session.add(maintainer_user)

        maintainer_user = await session.merge(maintainer_user)
        maintainer_role = await session.merge(maintainer_role)

    yield maintainer_user, maintainer_role


@pytest_asyncio.fixture
async def valid_user_credentials(async_session):
    username = "ValidUser"
    password = "validsafepassword1"

    me_permission = Permissions(
        id=UUID("1d5228c8-7934-4370-b4a1-f56ae802075a"),
        name="me",
        description="List all the user's details",
    )
    valid_role = Role(
        id=UUID("95ad20b5-473d-4255-830a-a7df94eb338d"),
        name="ValidRole",
        description="Valid role description",
        permissions=[me_permission],
    )
    valid_user = User(
        id=UUID("c8ee39f7-2213-4118-b0a6-2f8c0e882239"),
        name=username,
        full_name="Engineer Credentials",
        email="engineer.credentials@rfs-example.com",
        password=get_password_hash(password),
        groups=[],
        role_id=valid_role.id,
    )

    async with async_session() as session:
        session.add(valid_role)

    async with async_session() as session:
        session.add(valid_user)

    yield username, password


@pytest_asyncio.fixture
async def valid_user_with_no_scopes(async_session):
    username = "ValidUserButNoScopes"
    password = "verysafepassword2"

    current_user = User(
        id=UUID("c8ee39f7-2213-4118-b0a6-2f8c0e882239"),
        name=username,
        full_name="Engineer Credentials",
        email="engineer.credentials@rfs-example.com",
        password=get_password_hash(password),
        groups=[],
        role_id=None,
    )

    async with async_session() as session:
        session.add(current_user)

    yield username, password


# Route testing


@pytest_asyncio.fixture
def client() -> TestClient:
    return TestClient(app=create_app())
