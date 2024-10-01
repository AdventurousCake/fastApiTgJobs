import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, BackgroundTasks
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html, get_redoc_html, get_swagger_ui_html
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from pydantic import AnyHttpUrl
from rich.logging import RichHandler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.PROJ.api.api_html import html_router
from src.PROJ.api.api_main import r_jobs, r_private
from src.PROJ.core.db import init_models, async_session_factory
from src.PROJ.core.limiter import limiter
from src.PROJ.service_pyrogram.main_scheduler import run

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],  # markup=True
    # handlers=[RichHandler(rich_tracebacks=True, console=console)],
)
# FORMAT = "%(message)s"
# logging.basicConfig(
#     level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(markup=True)]  # RichHandler()
# )

# init_logging()
log = logging.getLogger("rich")

scheduler = AsyncIOScheduler()
def schedule_jobs():
    logging.warning('add tasks for scheduler ONLY first_run')
    # scheduler.add_job(run, id="first_run")  # first run
    scheduler.add_job(run, "interval", seconds=3600, id="my_job_id")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start app
    await on_startup()
    yield

    # Close app
    await on_shutdown()


async def run_bg_tasks(background_tasks: BackgroundTasks):
    # background_tasks.add_task(write_log, message)
    pass


async def on_startup():
    # log.warning("skip db init; USE ALEMBIC\n")
    await init_models(drop=True)

    log.warning('[bold red]starting scheduler[/]', extra={"markup": True})

    # init scheduler
    schedule_jobs()
    scheduler.start()

    # init cache
    # redis = aioredis.from_url("redis://localhost")
    # redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    FastAPICache.init(InMemoryBackend())


async def on_shutdown():
    scheduler.shutdown()


app = FastAPI(
    title="⚙ My private app",
    debug=True,
    docs_url=None,  # rewrote to fix swagger ui js load
    redoc_url=None,
    lifespan=lifespan,
)


# fix for static load issues
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # swagger_js_url="https://fastly.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js", # unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",

        # swagger_ui_parameters={"customJs": "/static/swagger.js",}
        # swagger_favicon_url="/static/favicon.png"
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
# templates = Jinja2Templates(BASE_DIR / "templates")


session = async_session_factory
session_async = async_session_factory

origins: list[AnyHttpUrl] = [
    "http://localhost:8000",
    # "http://myfastapi7.ddns.net",
    "https://myfastapi7.ddns.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
    # ["*"],
)

# LIMIT
from slowapi import _rate_limit_exceeded_handler

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app.include_router(main_router)
app.include_router(html_router)
app.include_router(r_private)
app.include_router(r_jobs)
# app.include_router(r_jwt)

# app.add_api_route("/jobs", jobs_html, methods=["GET"])


def api_run():
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")  # log_level="info" # host="0.0.0.0", port=80


if __name__ == "__main__":
    api_run()
