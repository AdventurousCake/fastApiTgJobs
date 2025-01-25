import logging

from fastapi import Query, Depends, APIRouter
from fastapi_cache.decorator import cache

from src.PROJ.api.schemas_jobs import SHr, VacancyData
from src.PROJ.core.dependencies import filter_params
from src.PROJ.core.limiter import limiter
from src.PROJ.db.db_repository_jobs import JobsDataRepository, HrDataRepository

log = logging.getLogger(__name__)
"""type: str = Query(None, max_length=100)"""
"""CommonsDep = Annotated[dict, Depends(common_parameters)]"""

r_jobs = APIRouter(prefix="/jobs", tags=["Jobs"], dependencies=None)

@cache(expire=60)
@r_jobs.get("/jobs_all", response_model=list[VacancyData])
async def jobs_all(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0),
                   ordering: str = Query(None)):
    data = await JobsDataRepository.get_all(limit=limit, offset=offset)
    return data


@cache(expire=60)
@r_jobs.get("/hrs_all", response_model=list[SHr])
async def hrs_all(params=Depends(filter_params)):
    data = await HrDataRepository.get_all(**params)
    return data

# @r_jobs.get('/')
# async def get_filtered(request: Request, params=Depends(filter_params)):
#     data = await JobsDataRepository.get_all(**params)
#     return [m.to_dict() for m in data]

# tst endpoints shelf
