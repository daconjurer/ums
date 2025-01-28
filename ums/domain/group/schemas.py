from ums.domain.data_access.interfaces import Schema


class GroupPublic(Schema):
    name: str
    description: str | None
