from rich.logging import RichHandler
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
    # DATABASE_PARAMS = {}
else:
    DATABASE_URL = config.DB_URL
    DATABASE_PARAMS = {}

logging.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nMODE: {config.MODE}\n{DATABASE_URL}\n\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

engine_async = create_async_engine(DATABASE_URL, echo=True, **DATABASE_PARAMS)
async_session_factory = async_sessionmaker(engine_async, expire_on_commit=False)  # ASYNC WITH!


async def init_models(drop=False):
    async with engine_async.begin() as conn:
        if drop:
            logging.warning("!drop db")
            await conn.run_sync(Base.metadata.drop_all)

        # engine_sync.echo = True
        # Base.metadata.create_all(engine_sync)

        await conn.run_sync(Base.metadata.create_all)

        print(f"INIT {DATABASE_URL}; tables in metadata:")
        _table_names = [
            table_name for table_name in Base.metadata.tables.keys()]
        for table_name in _table_names:
            print(table_name)

        # other METADATA
        # await conn.run_sync(metadata.create_all)


FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


async def create_db_and_tables():
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
