import sys

from ums.core.filter_sort import SortOptions
from ums.domain.entities import Group
from ums.domain.group.reader import group_reader
from ums.domain.group.writer import group_writer
from ums.domain.service.domain import DomainService

if sys.version_info > (3, 11):
    from datetime import UTC
else:
    from datetime import timezone

    UTC = timezone.utc


class GroupSortOptions(SortOptions):
    created_at = "created_at"
    updated_at = "updated_at"


class GroupService(DomainService[Group]):
    reader = group_reader
    writer = group_writer

    # async def add_user(
    #     self,
    #     user_create: UserCreate,
    #     hashing_function: Callable[[str], str] = get_password_hash,
    # ) -> User | None:
    #     # Validate user
    #     validated_user = await UserValidator().validate(self.db, user_create)

    #     # Hash password
    #     validated_user.password = hashing_function(validated_user.password)

    #     # Create record
    #     async with self.db() as session:
    #         user = await user_writer.create(session, validated_user)
    #         await session.commit()
    #         return user

    # async def update_user(
    #     self,
    #     user_update: UserUpdate,
    #     hashing_function: Callable[[str], str] = get_password_hash,
    # ) -> User | None:
    #     # Check if user exists
    #     user = await user_reader.get(self.db, user_update.id)

    #     if not user:
    #         raise exceptions.InvalidUserException()

    #     # Validate user
    #     validated_user = await UserValidator().validate(self.db, user_update)

    #     # Start updates
    #     update_timestamp = datetime.now(tz=UTC)

    #     # Hash password
    #     if validated_user.password:
    #         validated_user.password = hashing_function(validated_user.password)

    #     # Update verification timestamp
    #     if validated_user.is_verified:
    #         validated_user.verified_at = update_timestamp

    #     # Update updated timestamp
    #     validated_user.updated_at = update_timestamp

    #     # Update record
    #     async with self.db() as session:
    #         user = await user_writer.create(session, validated_user)
    #         await session.commit()
    #         return user

    # async def get_user_by_name(
    #     self,
    #     name: str,
    # ) -> User | None:
    #     user = await user_reader.get_by(
    #         db=self.db,
    #         filter=UserFilterParams(name=name),
    #     )
    #     return user

    # async def get_user_role_id(
    #     self,
    #     name: str,
    # ) -> UUID | None:
    #     """Get the role_id of a user."""
    #     user = await user_reader.get_by(
    #         db=self.db,
    #         filter=UserFilterParams(name=name),
    #     )
    #     if user:
    #         return user.role_id
    #     return None

    # async def get_users(
    #     self,
    #     filter: UserFilterParams,
    #     sort: SortParams,
    #     limit: int,
    #     page: int,
    # ) -> list[User]:
    #     return await user_reader.get_many(
    #         db=self.db,
    #         filter=filter,
    #         sort=sort,
    #         limit=limit,
    #         page=page,
    #     )
