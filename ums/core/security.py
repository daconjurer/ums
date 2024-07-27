from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from ums.settings.application import get_app_settings

security_settings = get_app_settings().security


def verify_password(plain_password, hashed_password) -> bool:
    verified = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return verified


def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=security_settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.secret_key,
        algorithm=security_settings.hashing_algorithm,
    )
    return encoded_jwt
