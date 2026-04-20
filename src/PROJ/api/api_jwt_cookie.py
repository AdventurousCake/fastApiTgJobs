from datetime import timedelta, datetime

import jwt
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.PROJ.core import config

r_jwt = APIRouter(prefix="/jwt", tags=["JWT"], dependencies=None)


# ===================================== JWT AUTH
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=config.JWT_KEY, algorithm=config.JWT_ALGORITHM)  # HS256
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        decoded = jwt.decode(jwt=token, key=config.JWT_KEY, algorithms=config.JWT_ALGORITHM)

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # if decoded.get("exp") < datetime.utcnow().timestamp():
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return decoded


def get_token(request: Request):
    token = request.cookies.get("jwt_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token

# raw
@r_jwt.get("/jwt-decode")
async def jwt_decode(request: Request, token: str = Depends(get_token)):
    # return token
    return decode_access_token(token)


@r_jwt.post("/jwt-create")
async def jwt_create(response: Response):  # user_data: SUserAuthData):
    # user = await authenticate_user(user_data.email, user_data.password)
    # if not user:
    #     raise IncorrectEmailOrPassword

    access_token = create_access_token(
        {"sub": str(999)})  # by user id; {"exp": datetime.utcnow() + timedelta(minutes=30)}

    response.set_cookie("jwt_access_token", access_token, httponly=True)
    return dict(access_token=access_token)


# todo
# @r_sec.post('/register')
# async def register(user_data: SUserAuthData):
#     user = await authenticate_user(user_data.email, user_data.password)
#     if not user:
#         raise IncorrectEmailOrPassword
#     access_token = create_access_token(
#         {"sub": str(user.id)})  # by user id; {"exp": datetime.utcnow() + timedelta(minutes=30)}
#     return dict(access_token=access_token)
