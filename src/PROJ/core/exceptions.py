from fastapi import HTTPException
from starlette import status


class BaseException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "user exists"


UserAlreadyExistsException2 = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user exists")

IncorrectEmailOrPassword = HTTPException(status.HTTP_401_UNAUTHORIZED)

TokenExpiredException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
