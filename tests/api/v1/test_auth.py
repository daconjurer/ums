from fastapi.testclient import TestClient

from tests.fixtures import (
    client,  # noqa F401
    db,  # noqa F401
    initialized_engineer_credentials,  # noqa F401
    initialized_groups,  # noqa F401
    initialized_permissions,  # noqa F401
    initialized_role_with_no_permissions,  # noqa F401
    initialized_roles,  # noqa F401
    initialized_user_with_no_scopes,  # noqa F401
    setup_and_teardown_db,  # noqa F401
)


class TestUserRoute:
    def setup_method(self):
        self.url = "/login"

    def test_login_for_access_token_with_non_existing_user(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        ...

        # test
        response = client.post(
            url=self.url,
            data={"username": "admin", "password": "admin"},
        )

        # validation
        assert response.status_code == 404

    def test_login_for_access_token_with_valid_credentials(
        self,
        client: TestClient,  # noqa F811
        initialized_engineer_credentials,  # noqa F811
    ):
        # setup
        username, password = initialized_engineer_credentials

        # test
        response = client.post(
            url=self.url,
            data={"username": username, "password": password},
        )

        # validation
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_for_access_token_with_invalid_credentials(
        self,
        client: TestClient,  # noqa F811
        initialized_engineer_credentials,  # noqa F811
    ):
        # setup
        username, _ = initialized_engineer_credentials

        # test
        response = client.post(
            url=self.url,
            data={"username": username, "password": "password"},
        )

        # validation
        assert response.status_code == 404

    def test_login_for_access_token_with_no_scopes(
        self,
        client: TestClient,  # noqa F811
        initialized_user_with_no_scopes,  # noqa F811
    ):
        # setup
        username, password = initialized_user_with_no_scopes

        # test
        response = client.post(
            url=self.url,
            data={"username": username, "password": password},
        )

        # validation
        assert response.status_code == 403
