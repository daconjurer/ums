import sys
from datetime import datetime
from typing import Callable
from uuid import UUID

from ums.core.service.domain import DomainService
from ums.core.utils.filter_sort import SortOptions, SortParams
from ums.core.utils.security import get_password_hash
from ums.domain import exceptions
from ums.domain.entities import User
from ums.domain.user.reader import UserFilterParams, user_reader
from ums.domain.user.schemas import UserCreate, UserUpdate
from ums.domain.user.validator import UserValidator
from ums.domain.user.writer import user_writer

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc


class UserSortOptions(SortOptions):
    full_name = "full_name"
    created_at = "created_at"
    updated_at = "updated_at"


class UserService(DomainService[User]):
    reader = user_reader
    writer = user_writer

    async def add_user(
        self,
        user_create: UserCreate,
        hashing_function: Callable[[str], str] = get_password_hash,
    ) -> User | None:
        # Validate user
        validated_user = await UserValidator().validate(self.db, user_create)

        # Hash password
        validated_user.password = hashing_function(validated_user.password)

        # Create record
        async with self.db() as session:
            user = await self.writer.create(session, validated_user)
            await session.commit()
            return user

    async def update_user(
        self,
        user_update: UserUpdate,
        hashing_function: Callable[[str], str] = get_password_hash,
    ) -> User | None:
        # Check if user exists
        user = await self.reader.get(self.db, user_update.id)

        if not user:
            raise exceptions.InvalidUserException()

        # Validate user
        validated_user = await UserValidator().validate(self.db, user_update)

        # Start updates
        update_timestamp = datetime.now(tz=UTC)

        # Hash password
        if validated_user.password:
            validated_user.password = hashing_function(validated_user.password)

        # Update verification timestamp
        if validated_user.is_verified:
            validated_user.verified_at = update_timestamp

        # Update updated timestamp
        validated_user.updated_at = update_timestamp

        # Update record
        async with self.db() as session:
            user = await self.writer.update(session, validated_user)
            await session.commit()
            return user

    async def get_user_by_name(
        self,
        name: str,
    ) -> User | None:
        user = await self.reader.get_by(
            db=self.db,
            filter=UserFilterParams(name=name),
        )
        return user

    async def get_user_role_id(
        self,
        name: str,
    ) -> UUID | None:
        """Get the role_id of a user."""
        user = await self.reader.get_by(
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
        return await self.reader.get_many(
            db=self.db,
            filter=filter,
            sort=sort,
            limit=limit,
            page=page,
        )
