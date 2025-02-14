from ums.core.data_access.writer import GenericWriter
from ums.domain.entities import Group


class GroupWriter(GenericWriter[Group]):
    model = Group


group_writer = GroupWriter()
