from ums.data_access.writer import GenericWriter
from ums.domain.entities import Permissions


class PermissionsWriter(GenericWriter[Permissions]):
    model = Permissions


permissions_writer = PermissionsWriter()
