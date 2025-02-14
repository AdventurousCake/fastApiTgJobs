import logging

import uvicorn
from rich.logging import RichHandler

from src.PROJ.api.create_fastapi_app import create_app
from src.PROJ.api.routers_jobs import r_jobs
from src.PROJ.users.user_routers import router_users

logging.basicConfig(level="INFO",
    format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)],  # markup=True
)
# logging.basicConfig(level="NOTSET",format="%(message)s",datefmt="[%X]",handlers=[RichHandler(markup=True)]#Handler())
# init_logging()
log = logging.getLogger("rich")

app = create_app()

# ROUTERS
app.include_router(router_users)
app.include_router(r_jobs)
# app.include_router(r_jwt)
# app.add_api_route("/jobs", jobs_html, methods=["GET"])


def api_run():
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")


if __name__ == "__main__":
    api_run()
