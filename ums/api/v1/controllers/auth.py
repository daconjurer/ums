from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from loguru import logger
from pydantic import BaseModel, ValidationError

from ums.api.v1.controllers import user as user_controller
from ums.core import exceptions
from ums.core.security import verify_password
from ums.models import User
from ums.settings.application import get_app_settings

security_settings = get_app_settings().security


# It checks that the Authorization header in a request contains a JWT token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items.",
        "users": "Read users.",
    },
)


class TokenData(BaseModel):
    name: str
    scopes: list[str] = []


def authenticate_user(name: str, password: str) -> User:
    user = user_controller.get_user_by_name(name)
    if not user:
        raise exceptions.AuthenticationException("User not found")
    if not verify_password(password, user.password):
        raise exceptions.AuthenticationException("Incorrect password")
    return user


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(
            token,
            security_settings.secret_key,
            algorithms=[security_settings.hashing_algorithm],
        )
        name: str | None = payload.get("sub")

        if not name:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, name=name)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = user_controller.get_user_by_name(name=token_data.name)
    if not user:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logger.warning(f"User {name} does not have enough permissions.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return current_user
