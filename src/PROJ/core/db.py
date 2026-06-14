import logging
import os
from typing import AsyncGenerator, Annotated

from sqlalchemy import NullPool, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.PROJ.core import config

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {str_256: String(256)}

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

if config.MODE == "TEST":
    DATABASE_URL = config.TEST_DB_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = config.DB_URL
    DATABASE_PARAMS = {}

logging.warning(f"[DB] !!!!!!!!!!!!!!!!\n"
                f"[DB] MODE: {config.MODE}\n{DATABASE_URL}\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

engine_async = create_async_engine(DATABASE_URL, echo=False, **DATABASE_PARAMS)
async_session_factory = async_sessionmaker(engine_async, expire_on_commit=False)  # ASYNC WITH

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def init_models(drop=False):
    async with engine_async.begin() as conn:
        if drop:
            logging.warning("[DB] DROP db")
            await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

        _table_names = [table_name for table_name in Base.metadata.tables.keys()]
        _table_names = ", ".join(_table_names)
        logging.warning(f"[DB] INIT {DATABASE_URL}; tables in metadata:\n"
                        f"{_table_names}")

        # other METADATA
        # await conn.run_sync(metadata.create_all)


async def create_db_and_tables():
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
