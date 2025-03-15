from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ums.api.auth import get_current_active_user
from ums.core.db.async_session import AsyncSessionStream, db
from ums.domain.entities import User

router = APIRouter(tags=["status"])


@router.get("/status")
async def read_system_status(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSessionStream = Depends(db),
):
    async with db() as session:
        logger.debug("Checking database connection.")
        try:
            await session.execute(text("SELECT 1"))
            return {"status": "OK"}
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
