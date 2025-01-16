import contextlib

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from src.PROJ.core.db import get_async_session
from src.PROJ.users.user_main import get_user_db, get_user_manager
from src.PROJ.users.user_schemas import UserCreate

"""https://fastapi-users.github.io/fastapi-users/latest/cookbook/create-user-programmatically/"""

# Превращаем асинхронные генераторы в асинхронные менеджеры контекста.
get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_superuser(email: EmailStr, username: str, password: str):
    await create_user(email, username, password, is_superuser=True)


async def create_user(email: EmailStr, username: str, password: str, is_superuser: bool = False):
    """Получение объекта асинхронной сессии.
    Получение объекта класса SQLAlchemyUserDatabase.
    Получение объекта класса UserManager.
    Создание пользователя.
    """
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            username=username,
                            email=email,
                            password=password,
                            is_superuser=is_superuser
                        )
                    )
    except UserAlreadyExists:
        pass
