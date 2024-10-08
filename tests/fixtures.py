from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from ums.core.app_factory import create_app
from ums.core.security import get_password_hash
from ums.db.session import drop_db, get_session, setup_db
from ums.models import Group, Permissions, Role, User


@pytest.fixture(autouse=True)
def db():
    return next(get_session())


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    setup_db()
    yield
    drop_db()


@pytest.fixture
def initialized_permissions(db):
    setup_db()

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

    db.add(users_permission)
    db.add(me_permission)
    db.commit()
    db.refresh(users_permission)
    db.refresh(me_permission)

    yield users_permission, me_permission


@pytest.fixture
def initialized_roles(db, initialized_permissions):
    users_permission, me_permission = initialized_permissions

    setup_db()

    role_admin = Role(
        id=UUID("30ba096f-1d1a-4d6e-bd35-0d2c83a6dc7b"),
        name="Admin",
        description="Admin role description",
        permissions=[users_permission, me_permission],
    )
    role_maintainer = Role(
        id=UUID("7995971c-a9a7-4737-a440-cf0bf2ae353c"),
        name="Maintainer",
        description="Maintainer role description",
        permissions=[me_permission],
    )
    role_user = Role(
        id=UUID("67276d92-b3d8-40c6-b5b6-327add57796a"),
        name="User",
        description="User role description",
    )

    db.add(role_admin)
    db.add(role_maintainer)
    db.add(role_user)
    db.commit()
    db.refresh(role_admin)
    db.refresh(role_maintainer)
    db.refresh(role_user)

    yield role_admin, role_maintainer, role_user


@pytest.fixture
def initialized_groups(db):
    setup_db()

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

    db.add(test_group_1)
    db.add(test_group_2)
    db.add(test_group_3)
    db.commit()
    db.refresh(test_group_1)
    db.refresh(test_group_2)
    db.refresh(test_group_3)

    yield test_group_1, test_group_2, test_group_3


@pytest.fixture
def initialized_users(db):
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

    db.add(test_user_1)
    db.add(test_user_2)
    db.add(test_user_3)
    db.add(test_user_4)
    db.commit()
    db.refresh(test_user_1)
    db.refresh(test_user_2)
    db.refresh(test_user_3)
    db.refresh(test_user_4)

    yield test_user_1, test_user_2, test_user_3, test_user_4


@pytest.fixture
def initialized_admin(db, initialized_groups, initialized_roles):
    group_alpha, _, _ = initialized_groups
    admin_role, _, _ = initialized_roles

    current_user = User(
        id=UUID("6dd0434c-ca7f-4454-8bb8-d589b8a0ce99"),
        name="TheAdmin",
        full_name="The Admin",
        email="the.admin@rfs-example.com",
        password=get_password_hash("adminspassword1"),
        groups=[group_alpha],
        role_id=admin_role.id,
    )
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    yield current_user, admin_role


@pytest.fixture
def initialized_maintainer(db, initialized_groups, initialized_roles):
    group_alpha, _, _ = initialized_groups
    _, maintainer_role, _ = initialized_roles

    current_user = User(
        id=UUID("ea1a76c1-3a1e-4952-a190-d510843b36a7"),
        name="TheMaintainer",
        full_name="The Maintainer",
        email="the.maintainer@rfs-example.com",
        password=get_password_hash("maintainerspassword1"),
        groups=[group_alpha],
        role_id=maintainer_role.id,
    )
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    yield current_user, maintainer_role


@pytest.fixture
def initialized_engineer(db, initialized_groups, initialized_roles):
    group_alpha, _, _ = initialized_groups
    _, _, engineer_role = initialized_roles

    current_user = User(
        id=UUID("8ada3a8b-67d4-4522-bb8f-67da31a7d629"),
        name="TheEngineer",
        full_name="The Engineer",
        email="the.engineer@rfs-example.com",
        password=get_password_hash("engineerspassword1"),
        groups=[group_alpha],
        role_id=engineer_role.id,
    )
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    yield current_user, engineer_role


@pytest.fixture
def initialized_engineer_credentials(db, initialized_groups, initialized_roles):
    group_alpha, _, _ = initialized_groups
    _, _, engineer_role = initialized_roles

    username = "TheEngineerAndCredentials"
    password = "engineerspassword1"

    current_user = User(
        id=UUID("c8ee39f7-2213-4118-b0a6-2f8c0e882239"),
        name=username,
        full_name="Engineer Credentials",
        email="engineer.credentials@rfs-example.com",
        password=get_password_hash(password),
        groups=[group_alpha],
        role_id=engineer_role.id,
    )
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    yield username, password


@pytest.fixture
def initialized_role_with_no_permissions(db):
    role_no_permissions = Role(
        id=UUID("f1e3e5d7-0c1d-4d9b-bf6b-1b3a1c3b7e9b"),
        name="NoPermissions",
        description="Role with no permissions",
    )

    db.add(role_no_permissions)
    db.commit()
    db.refresh(role_no_permissions)

    yield role_no_permissions


@pytest.fixture
def initialized_user_with_no_scopes(
    db,
    initialized_groups,
):
    group_alpha, _, _ = initialized_groups

    username = "TheEngineerAndCredentialsButNoScopes"
    password = "engineerspassword1"

    current_user = User(
        id=UUID("c8ee39f7-2213-4118-b0a6-2f8c0e882239"),
        name=username,
        full_name="Engineer Credentials",
        email="engineer.credentials@rfs-example.com",
        password=get_password_hash(password),
        groups=[group_alpha],
        role_id=None,
    )
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    yield username, password


# Route testing


@pytest.fixture
def client() -> TestClient:
    return TestClient(app=create_app())
