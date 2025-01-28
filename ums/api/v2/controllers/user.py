from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security

from ums.api.auth import get_current_active_user
from ums.core.filter_sort import SortParams
from ums.domain.user.schemas import UserPublic
from ums.domain.user.service import User, UserFilterParams, UserService, UserSortOptions
from ums.middlewares.filter_sort import parse_sorting

router = APIRouter(tags=["user"])


@router.get("/users")
async def read_users(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["users"])],
    filter: Annotated[UserFilterParams, Depends()],
    sort: Annotated[SortParams, Depends(parse_sorting(UserSortOptions))],
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
) -> list[UserPublic]:
    users_public_info = []

    users_info = await UserService().get_users(
        filter=filter,
        sort=sort,
        limit=limit,
        page=page,
    )

    for user_info in users_info:
        users_public_info.append(UserPublic(**user_info.model_dump()))

    return users_public_info


@router.get("/users/me")
async def read_own_details(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
) -> UserPublic:
    return UserPublic(**current_user.model_dump())
