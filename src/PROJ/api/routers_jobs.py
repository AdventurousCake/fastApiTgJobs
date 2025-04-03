import asyncio
import logging

from fastapi import Query, Depends, APIRouter, status
from fastapi_cache.decorator import cache
from sqlalchemy import select, text

from src.PROJ.api.schemas_jobs import SHr, VacancyData
from src.PROJ.core.db import async_session_factory
from src.PROJ.core.dependencies import filter_params
from src.PROJ.core.limiter import limiter
from src.PROJ.db.db_repository_jobs import JobsDataRepository, HrDataRepository
from src.PROJ.db.models_jobs import Jobs
from src.PROJ.gtable.main_gtable import run_gtable
from src.PROJ.users.user_main import current_active_user

log = logging.getLogger(__name__)

r_jobs = APIRouter(prefix="/jobs", tags=["Jobs"], dependencies=None)

@cache(expire=60)
@r_jobs.get("/jobs_all", response_model=list[VacancyData])
@limiter.limit("100/minute")
async def jobs_all(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0),
                   ordering: str = Query(None)):
    data = await JobsDataRepository.get_all(limit=limit, offset=offset)
    return data


@cache(expire=60)
@r_jobs.get("/hrs_all", response_model=list[SHr])
@limiter.limit("100/minute")
async def hrs_all(params=Depends(filter_params)):
    data = await HrDataRepository.get_all(**params)
    return data

@cache(expire=60)
@r_jobs.get("/search", response_model=list[VacancyData], dependencies=[Depends(current_active_user)])
@limiter.limit("100/minute")
async def search_vacancies(by_text: str = Query(None, min_length=3, max_length=255)):
    async with async_session_factory() as session:
        q = select(Jobs).filter(Jobs.text_.ilike(f"%{by_text}%"))
        result = await session.execute(q)
        data = result.unique().scalars().all()
        return data

@r_jobs.get('/status')
async def status():
    return status.HTTP_200_OK

@r_jobs.get('/robots.txt')
async def status():
    return "User-agent: *\nDisallow: /"

# @r_jobs.get('/hr/{hr_id}', response_model=SHr)
# async def hr_by_id(hr_id: int, params=Depends(filter_params)):
#     data = await HrDataRepository.get_by_id(hr_id, **params)
#     return data

# @r_jobs.get('/job/{job_id}', response_model=VacancyData)
# async def job_by_id(job_id: int, params=Depends(filter_params)):
#     data = await JobsDataRepository.get_by_id(job_id, **params)
#     return data

@r_jobs.get("/webhook-run", dependencies=[Depends(current_active_user)])
@limiter.limit("5/minute")
async def webhook():
    run = asyncio.create_task(run_gtable())
    run.add_done_callback(lambda x: log.info("gtable webhook run done"))
    return status.HTTP_200_OK

# tst endpoints shelf
