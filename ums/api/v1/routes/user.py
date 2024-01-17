from fastapi import APIRouter, Depends, Security, Query

from typing import Annotated

from ums.models import User
from ums.api.v1.controllers.auth import get_current_active_user
from ums.crud.user.repository import user_repository, UserSortByEnum, UserFilterByEnum
from ums.middlewares.filter_sort import SortBy, FilterBy, parse_sort, parse_filter
from ums.db.session import get_session
from ums.api.v1.controllers import user


router = APIRouter(tags=["user"])


@router.get("/users")
async def read_users(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["users"])],
    filter: list[FilterBy] | None = Depends(
        parse_filter([member.value for member in UserFilterByEnum])
    ),
    sort: SortBy | None = Depends(
        parse_sort([member.value for member in UserSortByEnum])
    ),
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
) -> list[user.UserPublic]:
    users_public_info = []

    users_info = user_repository.get_many(
        db=next(get_session()),
        filter=filter,
        sort=sort,
        limit=limit,
        page=page,
    )

    for user_info in users_info:
        users_public_info.append(user.get_user_public_info(user_info))

    return users_public_info


@router.get("/users/me")
async def read_own_details(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
) -> user.UserPublic:
    return user.get_user_public_info(current_user)
