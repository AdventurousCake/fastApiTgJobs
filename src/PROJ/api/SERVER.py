import uvicorn

from src.PROJ.api.app import app


def api_run():
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")  # log_level="info" # host="0.0.0.0", port=80


if __name__ == "__main__":
    api_run()