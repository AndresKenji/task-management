from fastapi import status
from fastapi.exceptions import HTTPException


class LoginRedirectException(HTTPException):
    """Custom exception for login redirects"""
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="Login required"
        )

class InvalidDatabaseException(Exception):
    pass