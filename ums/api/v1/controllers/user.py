from uuid import UUID

from pydantic import BaseModel, EmailStr

from ums.crud.user.repository import User, UserFilterParams, user_repository
from ums.db.async_connection import AsyncDatabaseSession


class UserPublic(BaseModel):
    name: str
    full_name: str | None
    email: EmailStr
    is_verified: bool


def get_user_public_info(user) -> UserPublic:
    public_user_info = UserPublic(
        name=user.name,
        full_name=user.full_name,
        email=user.email,
        is_verified=user.is_verified,
    )
    return public_user_info


async def get_user_by_name(name: str, db: AsyncDatabaseSession) -> User | None:
    user = await user_repository.get_by(
        db=db,
        filter=UserFilterParams(name=name),
    )
    return user


async def get_user_role_id(name: str, db: AsyncDatabaseSession) -> UUID | None:
    """Get the role_id of a user."""
    user = await user_repository.get_by(
        db=db,
        filter=UserFilterParams(name=name),
    )
    if user:
        return user.role_id
    return None
