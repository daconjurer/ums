import asyncio
from uuid import UUID

from ums.core.utils.security import get_password_hash
from ums.core.db.async_connection import DatabaseManager, create_custom_engine, get_async_session
from ums.domain.entities import Group, Permissions, Role, User

from ums.settings.application import get_app_settings

db_settings = get_app_settings().db


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
items_permission = Permissions(
    id=UUID("ddb249ad-781a-454d-a5bf-02cad7133216"),
    name="items",
    description="List all the user's items",
)

group_alpha = Group(
    id=UUID("d2ae3068-f5c3-4ab8-a1fd-912828963749"),
    name="Alpha",
    location="Mexico City",
)
group_delta = Group(
    id=UUID("190212f3-35fe-48d2-a3bc-320eee2f0d52"),
    name="Delta",
    location="Quito",
)

role_admin = Role(
    id=UUID("0f137fa1-d083-4e49-8b43-a333e93c84e4"),
    name="Admin",
    description="The admin role",
    permissions=[users_permission, me_permission, items_permission],
)
role_maintainer = Role(
    id=UUID("7a5221ec-6a18-4eca-83cf-64aa18a4e106"),
    name="Maintainer",
    description="The maintainer role",
    permissions=[me_permission, items_permission],
)
role_engineer = Role(
    id=UUID("f5909109-730c-4701-bd72-f3f6459d9086"),
    name="Engineer",
    description="The engineer role",
    permissions=[items_permission],
)

user_1 = User(
    id=UUID("f18941a4-bb0e-444a-b6a0-a19509cc6089"),
    name="VicS",
    full_name="Victor Sandoval",
    email="victor.sandoval@rfs-example.com",
    password=get_password_hash("verysafepassword1"),
    groups=[group_alpha, group_delta],
    role_id=role_admin.id,
)
user_2 = User(
    id=UUID("9d7a39d8-4e25-4368-8bc9-8e795ffb9e04"),
    name="SebitoM",
    full_name="Sebastian Manzano",
    email="sebastian.manzano@rfs-example.com",
    password=get_password_hash("verysafepassword2"),
    groups=[group_alpha],
    role_id=role_maintainer.id,
)
user_3 = User(
    id=UUID("17187ad4-90e5-4987-af91-60e70c925761"),
    name="LupePintos",
    full_name="Guadalupe Pintos",
    email="lupe.pintos@rfs-example.com",
    password=get_password_hash("verysafepassword3"),
    groups=[group_delta],
    role_id=role_maintainer.id,
)
user_4 = User(
    id=UUID("2fe19756-b3dd-4ca4-9ea9-69852b15c255"),
    name="JohnyVals",
    full_name="Juan Valdez",
    email="juan.valdez@rfs-example.com",
    password=get_password_hash("verysafepassword4"),
    groups=[group_alpha],
    role_id=role_engineer.id,
)
user_5 = User(
    id=UUID("4b1f6422-d080-4263-89c7-001aa06adea2"),
    name="AnnR",
    full_name="Anna Rios",
    email="anna.rios@rfs-example.com",
    password=get_password_hash("verysafepassword5"),
    groups=[group_alpha],
    role_id=role_engineer.id,
)
user_6 = User(
    id=UUID("ae495835-ba47-4289-8d56-e11fd2cb4bbf"),
    name="TerryC",
    full_name="Terrance Clark",
    email="terry.clark@rfs-example.com",
    password=get_password_hash("verysafepassword6"),
    groups=[group_alpha],
    role_id=role_engineer.id,
)
user_7 = User(
    id=UUID("df1a9368-e5fc-4671-9a14-0cb8af8cd34e"),
    name="LucasM",
    full_name="Lucas Manuel",
    email="lucas.manuel@rfs-example.com",
    password=get_password_hash("verysafepassword7"),
    groups=[group_delta],
    role_id=role_engineer.id,
)
user_8 = User(
    id=UUID("b64f20b3-31ca-4545-86d1-e912f35cb715"),
    name="FrankyRivers",
    full_name="Frank Rivers",
    email="frank.rivers@rfs-example.com",
    password=get_password_hash("verysafepassword8"),
    groups=[group_delta],
    role_id=role_engineer.id,
)
user_9 = User(
    id=UUID("b7f8621c-a43b-4a93-8309-89abff4c63b7"),
    name="Pamela Chacon",
    full_name="PamelaCh",
    email="pamela.chacon@rfs-example.com",
    password=get_password_hash("verysafepassword9"),
    groups=[group_delta],
    role_id=role_engineer.id,
)
user_10 = User(
    id=UUID("c3b162a7-e0c1-43d1-a237-037de1c771fd"),
    name="TeddyB",
    full_name="Ted Bermudez",
    email="teddy.bermudez@rfs-example.com",
    password=get_password_hash("verysafepassword10"),
    groups=[group_delta],
    role_id=role_engineer.id,
)


async def init_db():
    engine = create_custom_engine(str(db_settings.uri))
    await DatabaseManager.drop_db(engine=engine)
    await DatabaseManager.setup_db(engine=engine)

    async with get_async_session() as session:
        session.add_all([users_permission, me_permission, items_permission])
        session.add_all([role_admin, role_maintainer, role_engineer])

    async with get_async_session() as session:
        session.add_all([group_alpha, group_delta])

    async with get_async_session() as session:
        session.add_all(
            [
                user_1,
                user_2,
                user_3,
                user_4,
                user_5,
                user_6,
                user_7,
                user_8,
                user_9,
                user_10,
            ]
        )


if __name__ == "__main__":
    asyncio.run(init_db())
