from typing import Any, Dict, Optional

from fastapi import HTTPException, status

# HTTP exceptions (meant to stop execution on the spot)


class UMSException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InvalidRoleException(UMSException):
    def __init__(
        self,
        detail: str = "Role not found.",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InvalidGroupException(UMSException):
    def __init__(
        self,
        detail: str = "Group not found.",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InvalidUserException(UMSException):
    def __init__(
        self,
        detail: str = "User not found.",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InvalidFilteringException(UMSException):
    def __init__(
        self,
        detail: str = "Duplicate values supplied for filtering.",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
