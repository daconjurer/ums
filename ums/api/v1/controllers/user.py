from pydantic import BaseModel, EmailStr

from ums.crud.user.repository import FilterBy, user_repository
from ums.db.session import get_session


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


def get_user_by_name(name: str):
    user = user_repository.get_by(
        db=next(get_session()),
        filter=FilterBy(key="name", value=name),
    )
    return user


def get_user_role_id(name: str) -> str | None:
    """Get the role_id of a user."""
    user = user_repository.get_by(
        db=next(get_session()),
        filter=FilterBy(key="name", value=name),
    )
    if user:
        return str(user.role_id)
    return None
