import logging
from datetime import datetime
from pathlib import Path

import orjson
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi_cache.decorator import cache
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.PROJ.core.dependencies import limit_offset
from src.PROJ.db.db_repository_jobs import JobsDataRepository

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
templates = Jinja2Templates(BASE_DIR / "templates")

html_router = APIRouter(prefix='', tags=["html"], dependencies=None)


@html_router.get("/jinja/{abc}", response_class=HTMLResponse)
async def read_item(request: Request, abc: str):
    return templates.TemplateResponse(request=request, name="FAST1.html", context={"abc": abc})


# http://localhost:8000/secure/jobs?limit=15
# @app.get("/jobs")
# @r_jobs.get("/page")
@html_router.get('/html/')
async def jobs_html(request: Request, paginator_params=Depends(limit_offset)):
    """js table"""

    data = await JobsDataRepository.get_all(**paginator_params)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empty data")

    tabledata1 = [m.to_dict() for m in data]

    # orjson
    tabledata_str = orjson.dumps(tabledata1).decode('utf-8')

    columns = [dict(title="Id", field="id"),
               dict(title="New", field="is_new", formatter="tickCross", formatterParams={
                   'allowEmpty': 'true',
                   'allowTruthy': 'true',
                   'tickElement': "🆕",
                   'crossElement': "",
                   # 'tickElement':"<i class='fa fa-check'></i>",
                   # 'crossElement':"<i class='fa fa-times'></i>",
               }
                    ),
               dict(title="Lvl", field="level"),
               dict(title="Remote", field="remote"),
               dict(title="Startup", field="startup"),
               dict(title="Text", field="text_"),
               dict(title="Contacts", field="contacts"),
               # dict(title="Posted at", field="posted_at"),
               # dict(title="Parsed at", field="parsed_at"),
               # dict(title="Updated at", field="updated_at"),
               dict(title="user_tg_id", field="user_tg_id"),
               # dict(title="Hr", field="hr"),
               # dict(title="Views", field="views"),
               # dict(title="Chat", field="chat_username"),
               # dict(title="Msg url", field="msg_url"),
               # dict(title="Button", field="button_url"),
               # dict(title="Date", field="date_ru"),
               dict(title="Username", field="username"),
               ]

    return templates.TemplateResponse(
        request=request, name="FAST1.html", context={"tabledata": tabledata_str, "columns": columns,
                                                     "data": tabledata1}
    )
