from ums.core.data_access.reader import GenericReader
from ums.domain.entities import Permissions


class PermissionsReader(GenericReader[Permissions]):
    model = Permissions


permissions_reader = PermissionsReader()
