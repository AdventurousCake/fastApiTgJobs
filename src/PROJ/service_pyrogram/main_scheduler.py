import asyncio
import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.PROJ.core.db import get_async_session
from src.PROJ.db.db_repository_jobs import JobsDataRepository, HrDataRepository
from src.PROJ.service_pyrogram.pyro_JOBS import ScrapeVacancies


async def run(session: AsyncSession = Depends(get_async_session)):
    data = await ScrapeVacancies().run()
    data_jobs = [m.model_dump() for m in data.get("all_messages")]
    data_hrs = data.get("hr_data")

    await JobsDataRepository().clean_isnew_flag(session)

    await HrDataRepository().upsert(session, data_hrs)
    res = await JobsDataRepository().upsert_or_ignore(session, data_jobs)
    return res
