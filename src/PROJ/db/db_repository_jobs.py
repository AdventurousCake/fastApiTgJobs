import logging

from asyncpg import UniqueViolationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.PROJ.db.models_jobs import Jobs, HR
from sqlalchemy import select, text, update

from src.PROJ.core.db import async_session_factory, get_async_session


class HrDataRepository:
    @classmethod
    async def get_all(cls, **filter_by) -> list[HR]:
        async with async_session_factory() as session:
            q = select(HR).filter_by(**filter_by)
            result = await session.execute(q)
            return result.unique().scalars().all()

    @classmethod
    async def upsert(cls, data):
        async with async_session_factory() as session:
            q = insert(HR).values(data)
            q = q.on_conflict_do_update(
                constraint='hr_pkey',
                set_=dict(
                    username=q.excluded.username,
                ),
            ).returning(HR.id)

            res = await session.execute(q)
            await session.commit()
            return res.scalars().all()


class JobsDataRepository:
    @classmethod
    async def get_all(cls, limit: int = 100, offset: int = None, **filter_by) -> list[Jobs]:
        async with async_session_factory() as session:
            q = select(Jobs).filter_by(**filter_by).limit(limit).offset(offset)
            print(q.compile(compile_kwargs={"literal_binds": True}))

            result = await session.execute(q)
            return result.unique().scalars().all()

    @classmethod
    async def add(cls, data: dict) -> int:
        async with async_session_factory() as session:
            try:
                q = insert(Jobs).values(data)
                q = q.on_conflict_do_nothing().returning(Jobs.id)

                res = await session.execute(q)
                # commit in end
                id = res.scalar()

            except IntegrityError as e:
                logging.error(e)

            except UniqueViolationError as e:
                logging.error(e)

            await session.flush()
            await session.commit()
            return id

    @classmethod
    async def add_many(cls):
        async with async_session_factory() as session:
            pass

    @classmethod
    async def upsert(cls, data: dict | list):
        """if list: значения должны быть однородными, кол-во полей одинаковое"""
        async with async_session_factory() as session:
            try:
                # session.add(jobs)

                if isinstance(data, list):
                    q = insert(Jobs).values(data)
                elif isinstance(data, dict):
                    q = insert(Jobs).values(**data)
                else:
                    raise ValueError(
                        "Data must be either a list of dictionaries or a single dictionary"
                    )

                """
                https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#specifying-the-target
                constraint argument is used to specify an index directly rather than inferring it.
                This can be the name of a UNIQUE constraint, a PRIMARY KEY constraint, or an INDEX:"""

                # text_
                q = q.on_conflict_do_update(
                    # constraint='idx_uniq_id_text', set_=dict(text_=q.excluded.text_)
                    # index_elements=('id', 'text_'), set_=dict(text_=q.excluded.text_) # dw
                    # index_elements=('id',), set_=dict(text_=q.excluded.text_)
                    # constraint='jobs_pkey',

                    index_elements=("msg_url", "text_"),  # Уникальность по msg_url и text_
                    set_=dict(
                        text_=q.excluded.text_,
                        updated_at=text("TIMEZONE('utc', now())"),
                        msg_url=q.excluded.msg_url,
                    ),
                ).returning(Jobs.id)

                print("\n", q.compile(compile_kwargs={"literal_binds": True}))
                res = await session.execute(q)

                ids = res.scalars().all()

                await session.flush()
                await session.commit()
                return ids[0] if len(ids) == 1 else ids

            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def upsert_or_ignore(cls, data: dict | list):
        """if list: значения должны быть однородными, кол-во полей одинаковое"""
        async with async_session_factory() as session:
            try:
                if isinstance(data, list):
                    q = insert(Jobs).values(data)
                elif isinstance(data, dict):
                    q = insert(Jobs).values(**data)
                else:
                    raise ValueError("Data must be either a list of dictionaries or a single dictionary")

                """
                https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#specifying-the-target
                constraint argument is used to specify an index directly rather than inferring it.
                This can be the name of a UNIQUE constraint, a PRIMARY KEY constraint, or an INDEX:"""

                # text_
                q = q.on_conflict_do_nothing(
                    index_elements=("msg_url", "text_"),  # v2
                ).returning(Jobs.id)

                print("\n", q.compile(compile_kwargs={"literal_binds": True}))
                res = await session.execute(q)

                ids = res.scalars().all()

                await session.flush()
                await session.commit()
                return ids[0] if len(ids) == 1 else ids

            except Exception as e:
                await session.rollback()

                # logging.debug("error", exc_info=True, extra={'locals': locals()})
                raise e

    @classmethod
    async def clean_isnew_flag(cls):
        async with async_session_factory() as session:
            # new_data = {"is_new": True}
            q = await session.execute(update(Jobs).where(Jobs.is_new == True)
                                      .values(is_new=False).returning(Jobs.id))
            await session.commit()
            return q.scalars().all()
