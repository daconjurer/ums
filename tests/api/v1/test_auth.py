from fastapi.testclient import TestClient

from tests.original_fixtures import (
    async_session,  # noqa F401
    client,  # noqa F401
    engine,  # noqa F401
    setup_and_teardown_db,  # noqa F401
    valid_user_credentials,  # noqa F401
    valid_user_with_no_scopes,  # noqa F401
)


class TestLoginRoute:
    def setup_method(self):
        self.url = "/login"

    async def test_login_for_access_token_with_non_existing_user(
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

    async def test_login_for_access_token_with_valid_credentials(
        self,
        client: TestClient,  # noqa F811
        valid_user_credentials,  # noqa F811
    ):
        # setup
        username, password = valid_user_credentials

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

    async def test_login_for_access_token_with_invalid_credentials(
        self,
        client: TestClient,  # noqa F811
        valid_user_credentials,  # noqa F811
    ):
        # setup
        username, _ = valid_user_credentials

        # test
        response = client.post(
            url=self.url,
            data={"username": username, "password": "password"},
        )

        # validation
        assert response.status_code == 404

    async def test_login_for_access_token_with_no_scopes(
        self,
        client: TestClient,  # noqa F811
        valid_user_with_no_scopes,  # noqa F811
    ):
        # setup
        username, password = valid_user_with_no_scopes

        # test
        response = client.post(
            url=self.url,
            data={"username": username, "password": password},
        )

        # validation
        assert response.status_code == 403
