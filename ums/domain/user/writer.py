from ums.core.data_access.writer import GenericWriter
from ums.domain.entities import User


class UserWriter(GenericWriter[User]):
    model = User


user_writer = UserWriter()
