from ums.domain.data_access.reader import GenericReader
from ums.domain.entities import Group


class GroupReader(GenericReader[Group]):
    model = Group


group_reader = GroupReader()
