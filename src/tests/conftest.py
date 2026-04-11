import asyncio
import logging
import random
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from src.PROJ.core.config import TEST_DB_URL
from src.PROJ.api.app import app
from src.PROJ.core.db import Base, get_async_session
from src.PROJ.users.user_models import User

# only sync
# from fastapi.testclient import TestClient
# client = TestClient(app)

logging.warning(f"TEST_DB_URL: {TEST_DB_URL}")
engine_test = create_async_engine(TEST_DB_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        # await session.rollback() # откат изменений

app.dependency_overrides[get_async_session] = override_get_async_session

def get_password_hash(password: str) -> str:
    from fastapi_users.password import PasswordHelper
    from pwdlib import PasswordHash, exceptions
    from pwdlib.hashers.argon2 import Argon2Hasher

    password_hash = PasswordHash((Argon2Hasher(),))
    password_helper = PasswordHelper(password_hash)
    return password_helper.hash(password)

async def create_test_users(session: AsyncSession):
    test_users = [
        {
            "email": "admin_pytest@test.com",
            "username": "admin_pytest",
            "password": "admin123",
            "is_superuser": True,
            "role_id": 1
        },
        {
            "email": "user@test.com",
            "username": "testuser",
            "password": "user123",
            "is_superuser": False,
            "role_id": 2
        }
    ]

    for user_data in test_users:
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            is_superuser=user_data["is_superuser"],
            # role_id=user_data["role_id"]
        )
        session.add(user)

    await session.commit()
    logging.debug(f"Test users created: {test_users}")

    q = await session.execute(select(User))
    logging.debug(f"All users: {q.scalars().all()}")


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        await create_test_users(session)

    # todo # pass session
    # await init_fake_data(limit=10)

    yield
    # clear
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine_test.dispose()

# @pytest.fixture(scope='session')
# async def generate_fake_data():
#     await init_fake_data(limit=10)

# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """async client fixture"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test_base") as ac:
        yield ac

# authorized_client
@pytest.fixture
async def test_user_token(ac: AsyncClient) -> str:
    response = await ac.post("/auth/jwt/login",
        data={"username": "testuser", "password": "user123"}
    )
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.fixture
async def authorized_client(ac: AsyncClient, test_user_token: str) -> AsyncClient:
    ac.headers["Authorization"] = f"Bearer {test_user_token}"
    logging.debug(ac)
    return ac