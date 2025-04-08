from fastapi import APIRouter, Depends, HTTPException

from src.PROJ.users.user_schemas import UserCreate, UserRead, UserUpdate

from src.PROJ.users.user_main import current_active_user, fastapi_users, auth_backend, current_superuser, \
    get_user_manager
from src.PROJ.users.user_models import User

router_users = APIRouter()

router_users.include_router(
    # В роутер аутентификации передается объект бэкенда аутентификации.
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
router_users.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router_users.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router_users.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router_users.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)


# method override
@router_users.delete('/users/{id}', tags=['users'], deprecated=True)
def delete_user(id: str):
    """Deactivate users instead of delete"""
    raise HTTPException(
        # 405 - method not allowed
        status_code=405,
        detail="Удаление пользователей запрещено!"
    )


@router_users.get("/users_all_su", dependencies=[Depends(current_superuser)])
async def get_users_all():
    ...


@router_users.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@router_users.get("/authenticated-route-admin")
async def authenticated_route(user: User = Depends(current_superuser)):
    return {"message": f"Hello admin {user.email}!"}
