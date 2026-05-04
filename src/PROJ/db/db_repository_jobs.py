import logging

from asyncpg import UniqueViolationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.PROJ.db.models_jobs import Jobs, HR
from sqlalchemy import select, text, update

from src.PROJ.core.db import async_session_factory, get_async_session


class HrDataRepository:
    def __init__(self, model=HR):
        self.model = model

    async def get_all(self, session: AsyncSession, **filter_by) -> list[HR]:
        q = select(self.model).filter_by(**filter_by)
        result = await session.execute(q)
        return result.unique().scalars().all()

    async def upsert(self, session, data):
        q = insert(self.model).values(data)
        q = q.on_conflict_do_update(
            constraint='hr_pkey',
            set_=dict(
                username=q.excluded.username,
            ),
        ).returning(self.model.id)

        res = await session.execute(q)
        await session.commit()
        return res.scalars().all()


class JobsDataRepository:
    def __init__(self, model=Jobs):
        self.model = model

    async def get_all(self, session, limit: int = 100, offset: int = None, **filter_by) -> list[Jobs]:
        q = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)

        result = await session.execute(q)

        return result.unique().scalars().all()
        # return result.mappings().all()

    async def add(self, session, data: dict) -> int:
        try:
            q = insert(self.model).values(data)
            q = q.on_conflict_do_nothing().returning(self.model.id)

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

    async def add_many(self,session):
        pass

    async def upsert(self, session, data: dict | list):
        """if list: значения должны быть однородными, кол-во полей одинаковое"""
        try:
            if isinstance(data, list):
                q = insert(self.model).values(data)
            elif isinstance(data, dict):
                q = insert(self.model).values(**data)
            else:
                raise ValueError("Data must be either a list of dictionaries or a single dictionary")

            """
            https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#specifying-the-target
            constraint argument is used to specify an index directly rather than inferring it.
            This can be the name of a UNIQUE constraint, a PRIMARY KEY constraint, or an INDEX:"""

            q = q.on_conflict_do_update(
                # index_elements=('id',), set_=dict(text_=q.excluded.text_)
                # constraint='jobs_pkey',
                constraint='idx_uniq_link_text',

                set_=dict(
                    text_=q.excluded.text_,
                    updated_at=text("TIMEZONE('utc', now())"),
                    msg_url=q.excluded.msg_url,
                ),
            ).returning(self.model.id)

            res = await session.execute(q)

            ids = res.scalars().all()

            await session.flush()
            await session.commit()
            return ids[0] if len(ids) == 1 else ids

        except Exception as e:
            await session.rollback()
            raise e

    async def upsert_or_ignore(self, session, data: dict | list):
        """if list: значения должны быть однородными, кол-во полей одинаковое"""
        try:
            if isinstance(data, list):
                q = insert(self.model).values(data)
            elif isinstance(data, dict):
                q = insert(self.model).values(**data)
            else:
                raise ValueError("Data must be either a list of dictionaries or a single dictionary")

            """
            https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#specifying-the-target
            constraint argument is used to specify an index directly rather than inferring it.
            This can be the name of a UNIQUE constraint, a PRIMARY KEY constraint, or an INDEX:"""

            q = q.on_conflict_do_nothing(constraint='idx_uniq_link_text').returning(self.model.id)

            # print("\n", q.compile(compile_kwargs={"literal_binds": True}))
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
    async def clean_isnew_flag(self, session):
        """new_data = {"is_new": True}"""
        
        async with async_session_factory() as session:
            q = await session.execute(update(Jobs).where(Jobs.is_new == True).values(is_new=False).returning(Jobs.id))
            await session.commit()
            return q.scalars().all()
