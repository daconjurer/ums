from datetime import timedelta

from fastapi.testclient import TestClient

from tests.fixtures import (
    async_session,  # noqa F401
    client,  # noqa F401
    engine,  # noqa F401
    initialized_admin,  # noqa F401  # noqa F401
    initialized_maintainer,  # noqa F401
    initialized_users,  # noqa F401
    setup_and_teardown_db,  # noqa F401
)
from ums.core.security import create_access_token


class TestUserRoute:
    def setup_method(self):
        self.url = "/users"

    def test_read_users_without_authorization(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        ...

        # test
        response = client.get(url=self.url)

        # validation
        assert response.status_code == 401

    def test_read_users_with_authorization(
        self,
        client,  # noqa F811
        initialized_users,  # noqa F811
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
        payload = response.json()

        assert response.status_code == 200

        for test_user, payload_user in zip(initialized_users, payload[:-1]):
            assert test_user.name == payload_user["name"]
            assert test_user.full_name == payload_user["full_name"]
            assert test_user.email == payload_user["email"]

        assert current_user.name == payload[-1]["name"]
        assert current_user.full_name == payload[-1]["full_name"]
        assert current_user.email == payload[-1]["email"]

    def test_read_users_with_filtering(
        self,
        client,  # noqa F811
        initialized_users,  # noqa F811
        initialized_admin,  # noqa F811
    ):
        # setup
        current_user, current_user_role = initialized_admin
        test_user_number = 3

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
            params={"filter": f"name:{initialized_users[test_user_number].name}"},
        )

        # validation
        payload = response.json()

        assert response.status_code == 200
        assert (
            initialized_users[test_user_number].name
            in payload[test_user_number]["name"]
        )

    def test_read_users_with_sorting(
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

        # tests
        response_asc = client.get(
            url=self.url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"sort": "full_name:asc"},
        )
        response_desc = client.get(
            url=self.url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"sort": "full_name:desc"},
        )

        # validation
        payload_asc = response_asc.json()
        payload_desc = response_desc.json()

        assert response_asc.status_code == 200

        for i in range(len(payload_asc) - 1):
            assert payload_asc[i]["full_name"] < payload_asc[i + 1]["full_name"]

        assert response_desc.status_code == 200

        for i in range(len(payload_desc) - 1):
            assert payload_desc[i]["full_name"] > payload_desc[i + 1]["full_name"]

    def test_read_users_with_limit_and_pagination(
        self,
        client,  # noqa F811
        initialized_users,  # noqa F811
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

        # tests
        response_page_1 = client.get(
            url=self.url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"page": 1, "limit": 3},
        )
        response_page_2 = client.get(
            url=self.url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"page": 2, "limit": 3},
        )

        # validation
        payload_page_1 = response_page_1.json()
        payload_page_2 = response_page_2.json()

        assert response_page_1.status_code == 200
        assert response_page_2.status_code == 200

        assert len(payload_page_1) == 3
        assert len(payload_page_2) == 2

    def test_read_own_details_without_authorization(
        self,
        client,  # noqa F811
        initialized_users,  # noqa F811
    ):
        # setup
        ...

        # test
        response = client.get(url="/users/me")

        # validation
        assert response.status_code == 401

    def test_read_own_details_with_authorization(
        self,
        client,  # noqa F811
        initialized_users,  # noqa F811
        initialized_maintainer,  # noqa F811
    ):
        # setup
        current_user, current_user_role = initialized_maintainer

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
            url=f"{self.url}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # validation
        payload = response.json()

        assert response.status_code == 200
        assert current_user.name == payload["name"]
        assert current_user.full_name == payload["full_name"]
        assert current_user.email == payload["email"]
