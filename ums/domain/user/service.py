from uuid import UUID

from ums.core.filter_sort import SortOptions, SortParams
from ums.domain.service.domain import DomainService
from ums.domain.user.reader import User, UserFilterParams, user_reader


class UserSortOptions(SortOptions):
    full_name = "full_name"
    created_at = "created_at"
    updated_at = "updated_at"


class UserService(DomainService[User]):
    async def get_user_by_name(
        self,
        name: str,
    ) -> User | None:
        user = await user_reader.get_by(
            db=self.db,
            filter=UserFilterParams(name=name),
        )
        return user

    async def get_user_role_id(
        self,
        name: str,
    ) -> UUID | None:
        """Get the role_id of a user."""
        user = await user_reader.get_by(
            db=self.db,
            filter=UserFilterParams(name=name),
        )
        if user:
            return user.role_id
        return None

    async def get_users(
        self,
        filter: UserFilterParams,
        sort: SortParams,
        limit: int,
        page: int,
    ) -> list[User]:
        return await user_reader.get_many(
            db=self.db,
            filter=filter,
            sort=sort,
            limit=limit,
            page=page,
        )
