import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.templating import Jinja2Templates
from pydantic import AnyHttpUrl
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.PROJ.api.docs_fix import register_static_docs_routes
from src.PROJ.core import config
from src.PROJ.core.db import init_models, engine_async
from src.PROJ.core.limiter import limiter
from src.PROJ.core.scheduler import schedule_jobs, start_scheduler, stop_scheduler
from src.PROJ.users.user_create_superuser import create_user

log = logging.getLogger("rich")

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
templates = Jinja2Templates(BASE_DIR / "templates")

async def on_startup():
    # log.warning("skip db init; ALEMBIC\n")
    await init_models(drop=True)

    log.warning('[bold red]create superuser admin@admin.com[/]', extra={"markup": True})
    await create_user(email='admin@admin.com', username='admin', password='admin', is_superuser=True)

    log.warning('[bold red]starting scheduler[/]', extra={"markup": True})

    # init scheduler
    schedule_jobs()
    start_scheduler()

    # init cache
    log.warning('[bold red]starting redis+cache[/]', extra={"markup": True})
    # redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    # FastAPICache.init(RedisBackend(redis), prefix="fa-cache")
    FastAPICache.init(InMemoryBackend())


async def on_shutdown():
    stop_scheduler()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    await on_startup()

    yield
    # shutdown
    await on_shutdown()


def create_app(create_custom_static_urls: bool = False) -> FastAPI:
    app = FastAPI(
        title="⚙ My app",
        debug=True,
        default_response_class=ORJSONResponse,

        lifespan=lifespan,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )
    if create_custom_static_urls:
        register_static_docs_routes(app)

    origins: list[AnyHttpUrl] = [
        "http://localhost:8000",
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

    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    # LIMIT
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # admin panel
    if config.ADMIN_PANEL_ENABLED:
        from src.PROJ.admin_panel.admin_views import UserAdmin, JobsAdmin
        from sqladmin import Admin

        admin = Admin(app, engine_async)
        admin.add_view(UserAdmin)
        admin.add_view(JobsAdmin)

    return app