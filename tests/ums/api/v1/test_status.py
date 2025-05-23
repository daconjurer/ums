from datetime import timedelta

from tests.fixtures.original_fixtures import (
    async_session,  # noqa F401
    client,  # noqa F401
    engine,  # noqa F401
    initialized_admin,  # noqa F401
    setup_and_teardown_db,  # noqa F401
)
from ums.core.utils.security import create_access_token


class TestStatusRoute:
    def setup_method(self):
        self.url = "/status"

    def test_check_status_with_authorization(
        self,
        client,  # noqa F811
        initialized_admin,  # noqa F811
    ):
        # setup
        current_user, current_user_role = initialized_admin

        access_token_expires = timedelta(minutes=1)
        user_scopes = [
            permissions.name for permissions in current_user_role.permissions
        ]
        access_token = create_access_token(
            data={"sub": current_user.name, "scopes": user_scopes},
            expire_delta=access_token_expires,
        )

        # test
        response = client.get(
            url=self.url,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # validation
        assert response.status_code == 200
