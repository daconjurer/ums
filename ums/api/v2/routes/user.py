from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security

from ums.api.v2.controllers import user
from ums.api.v2.controllers.auth import get_current_active_user
from ums.core.filter_sort import SortParams
from ums.db.async_session import AsyncSessionStream, db
from ums.domain.user.reader import (
    User,
    UserFilterParams,
    UserSortOptions,
    user_reader,
)
from ums.middlewares.filter_sort import parse_sorting

router = APIRouter(tags=["user"])


@router.get("/users")
async def read_users(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["users"])],
    db: Annotated[AsyncSessionStream, Depends(db)],
    filter: Annotated[UserFilterParams, Depends()],
    sort: Annotated[SortParams, Depends(parse_sorting(UserSortOptions))],
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
) -> list[user.UserPublic]:
    users_public_info = []

    users_info = await user_reader.get_many(
        db=db,
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
