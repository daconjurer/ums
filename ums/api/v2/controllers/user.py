from uuid import UUID

from pydantic import BaseModel, EmailStr

from ums.db.async_session import AsyncSessionStream
from ums.domain.user.reader import User, UserFilterParams, user_reader


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


async def get_user_by_name(
    name: str,
    db: AsyncSessionStream,
) -> User | None:
    user = await user_reader.get_by(
        db=db,
        filter=UserFilterParams(name=name),
    )
    return user


async def get_user_role_id(
    name: str,
    db: AsyncSessionStream,
) -> UUID | None:
    """Get the role_id of a user."""
    user = await user_reader.get_by(
        db=db,
        filter=UserFilterParams(name=name),
    )
    if user:
        return user.role_id
    return None
