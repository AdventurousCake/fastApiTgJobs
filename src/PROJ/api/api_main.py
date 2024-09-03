import logging
import pathlib

from fastapi import Query, Depends, APIRouter
from fastapi_cache.decorator import cache
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from src.PROJ.api.schemas_jobs import SHr, VacancyData
from src.PROJ.core.limiter import limiter
from src.PROJ.db.db_repository_jobs import JobsDataRepository, HrDataRepository

log = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent.parent
templates = Jinja2Templates(BASE_DIR / "templates")

"""type: str = Query(None, max_length=100)"""
"""CommonsDep = Annotated[dict, Depends(common_parameters)]"""

r_jobs = APIRouter(prefix="/jobs", tags=["📗 Jobs"], dependencies=None)
r_private = APIRouter(prefix="/private", tags=["🔐 private URLS"], dependencies=None)


def limit_offset2(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0)) -> dict:
    return {"limit": limit, "offset": offset}


def filter_params0(filter_by: str = Query(None), filter_value: str = Query(None)) -> dict:
    return {filter_by: filter_value}


def filter_params(filter_by: str = Query(None), filter_value: int = Query(None)) -> dict:
    return {filter_by: bool(filter_value)}


# @r_jobs.get('/')
# async def get_filtered(request: Request, params=Depends(filter_params)):
#     data = await JobsDataRepository.get_all(**params)
#     return [m.to_dict() for m in data]

@limiter.limit("5/minute")
@cache(expire=60)
@r_jobs.get("/jobs_all", response_model=list[VacancyData])
async def jobs_all(limit: int = Query(10, ge=0), offset: int = Query(None, ge=0)):
    data = await JobsDataRepository.get_all(limit=limit, offset=offset)
    return data


@limiter.limit("5/minute")
@cache(expire=60)
@r_jobs.get("/hrs_all", response_model=list[SHr])
async def hrs_all(request: Request, params=Depends(filter_params)):
    data = await HrDataRepository.get_all()
    return data

# tst shelf
