import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from src.PROJ.core.config import TEST_DB_URL
from src.PROJ.api.app import app

# DATABASE
# DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

class Base(DeclarativeBase):
    __abstract__ = True

    # type_annotation_map = {str_256: String(256)}

    repr_col_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__dict__):
            if idx < self.repr_col_num:
                cols.append(f"{col}={self.__dict__[col]}")
            else:
                break
        return f"<{self.__class__.__name__}({', '.join(cols)})>"

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


engine_test = create_async_engine(TEST_DB_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides['async_session_factory'] = override_get_async_session

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # todo
    # await init_fake_data(limit=10)

    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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

test_client = TestClient(app)

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac