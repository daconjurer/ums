import secrets

from ums.core.security import get_password_hash


def create_password(length: int = 8) -> str:
    return secrets.token_urlsafe(length)


def create_user_auth_config(password: str | None = None) -> dict[str, str]:
    config = {}
    config["password"] = password if password else create_password()
    config["password"] = get_password_hash(config["password"])

    return config


print(create_user_auth_config(password="your_password_goes_here"))
