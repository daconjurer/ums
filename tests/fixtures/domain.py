from uuid import UUID

import pytest_asyncio

from ums.core.utils.security import get_password_hash
from ums.domain.entities import Group, Permissions, Role, User


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
        await session.commit()

    async with async_session() as session:
        admin_role = await session.merge(admin_role)
        maintainer_role = await session.merge(maintainer_role)
        user_role = await session.merge(user_role)
        await session.commit()

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
        await session.commit()

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
        await session.commit()

    async with async_session() as session:
        test_user_1 = await session.merge(test_user_1)
        test_user_2 = await session.merge(test_user_2)
        test_user_3 = await session.merge(test_user_3)
        test_user_4 = await session.merge(test_user_4)
        await session.commit()

    yield test_user_1, test_user_2, test_user_3, test_user_4


@pytest_asyncio.fixture
async def initialized_user_with_role_and_groups(
    async_session,
    initialized_roles,
    # initialized_groups,  # TODO: Add this fixture
):
    test_role, _, _ = initialized_roles
    # test_group_1, _, _ = initialized_groups

    test_user_1 = User(
        id=UUID("f18941a4-bb0e-444a-b6a0-a19509cc6089"),
        name="vic",
        full_name="Victor Sandoval",
        email="victor.sandoval@rfs-example.com",
        password=get_password_hash("password1"),
        role_id=test_role.id,
        # groups=[test_group_1],
    )

    async with async_session() as session:
        session.add(test_user_1)
        await session.commit()

    yield test_user_1
