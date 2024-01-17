from datetime import datetime, timedelta

import logging
from jose import jwt
from passlib.context import CryptContext

from ums.settings.application import get_app_settings


security_settings = get_app_settings().security

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password) -> bool:
    logging.getLogger().setLevel(logging.ERROR)
    # Silence "AttributeError: module 'bcrypt' has no attribute '__about__'" warning log
    verified = pwd_context.verify(plain_password, password)
    logging.getLogger().setLevel(logging.INFO)
    return verified


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.secret_key,
        algorithm=security_settings.hashing_algorithm,
    )
    return encoded_jwt
