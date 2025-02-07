import uvicorn

from src.PROJ.api.app import app


def api_run():
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")


if __name__ == "__main__":
    api_run()