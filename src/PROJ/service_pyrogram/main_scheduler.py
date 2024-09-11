import asyncio
import logging

from src.PROJ.db.db_repository_jobs import JobsDataRepository, HrDataRepository
from src.PROJ.service_pyrogram.pyro_JOBS_NEW import ScrapeVacancies


async def run():
    data = await ScrapeVacancies().run()
    data_jobs = [m.model_dump() for m in data.get("all_messages")]
    data_hrs = data.get("hr_data")

    await JobsDataRepository.clean_isnew()

    await HrDataRepository.upsert(data_hrs)
    res = await JobsDataRepository.upsert_or_ignore(data_jobs)
    return res
