from typing import Annotated

from fastapi import APIRouter, Depends

from ums.api.v1.controllers.auth import get_current_active_user
from ums.models import User

router = APIRouter(tags=["status"])


@router.get("/status")
async def read_system_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return {"status": "OK"}
