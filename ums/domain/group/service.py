import sys

from ums.core.service.domain import DomainService
from ums.core.utils.filter_sort import SortOptions, SortParams
from ums.domain import exceptions
from ums.domain.entities import Group
from ums.domain.group.reader import GroupFilterParams, group_reader
from ums.domain.group.schemas import GroupCreate, GroupUpdate
from ums.domain.group.validator import GroupValidator
from ums.domain.group.writer import group_writer

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

    async def add_group(
        self,
        group_create: GroupCreate,
    ) -> Group | None:
        # Validate user
        validated_group = await GroupValidator().validate(self.db, group_create)

        # Create record
        async with self.db() as session:
            group = await group_writer.create(session, validated_group)
            await session.commit()
            return group

    async def update_group(
        self,
        group_update: GroupUpdate,
    ) -> Group | None:
        # Check if group exists
        group = await group_reader.get(self.db, group_update.id)

        if not group:
            raise exceptions.InvalidGroupException()

        # Validate group
        validated_group = await GroupValidator().validate(self.db, group_update)

        # Update record
        async with self.db() as session:
            group = await group_writer.update(session, validated_group)
            await session.commit()
            return group

    async def get_group_by_name(
        self,
        name: str,
    ) -> Group | None:
        group = await group_reader.get_by(self.db, GroupFilterParams(name=name))
        return group

    async def get_group_by_location(
        self,
        location: str,
    ) -> Group | None:
        group = await group_reader.get_by(self.db, GroupFilterParams(location=location))
        return group

    async def get_groups(
        self,
        filter: GroupFilterParams,
        sort: SortParams,
        limit: int,
        page: int,
    ) -> list[Group]:
        return await group_reader.get_many(
            self.db,
            filter=filter,
            sort=sort,
            limit=limit,
            page=page,
        )
