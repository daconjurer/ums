from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from pydantic import BaseModel

from ums.api.v1.controllers import permissions as permissions_controller
from ums.api.v1.controllers.auth import authenticate_user
from ums.core.security import create_access_token
from ums.db.async_connection import AsyncDatabaseSession, db
from ums.domain.exceptions import AuthenticationException
from ums.settings.application import get_app_settings

security_settings = get_app_settings().security

router = APIRouter(tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login")
async def login_for_access_token(
    db: Annotated[AsyncDatabaseSession, Depends(db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
    except AuthenticationException as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=security_settings.access_token_expire_minutes
    )

    # Check the role of the user
    if not user.role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no role assigned.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get the permissions for that role
    user_permissions = await permissions_controller.get_permissions_by_role_id(
        db=db,
        role_id=user.role_id,
    )

    user_scopes = [user_permission.name for user_permission in user_permissions]
    # Enable the two lines below for API/auth debugging
    # user_scopes = form_data.scopes
    # logger.debug(f"user_scopes: {user_scopes}")

    access_token = create_access_token(
        data={"sub": user.name, "scopes": user_scopes},
        expire_delta=access_token_expires,
    )

    logger.info(f"User {user.name} successfully logged in.")
    return Token(access_token=access_token, token_type="bearer")
