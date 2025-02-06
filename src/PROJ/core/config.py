import json
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv, find_dotenv
import os

# class Settings(BaseSettings):
#     app_title: str = 'app'
#     database_url: str
#     secret: str = 'SECRET'
#     class Config:
#         env_file = '.env'
# settings = Settings() 

# load from .env; относительно config.py
env_file = find_dotenv(".env")
env = load_dotenv(env_file)
if not env:
    logging.critical("!!! no .env file")

MODE = os.getenv("MODE")
if MODE == "DOCKER":
    DB_HOST = os.getenv("DB_HOST", "pg")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")

else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")

# for testing
TEST_DB_HOST = os.getenv("TEST_DB_HOST")
TEST_DB_PORT = os.getenv("TEST_DB_PORT")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASS = os.getenv("TEST_DB_PASS")
TEST_DB_URL = os.getenv("TEST_DB_URL")  # or full

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
if TEST_DB_HOST:
    TEST_DB_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
else:
    # Using env
    assert "+asyncpg" in TEST_DB_URL

# JWT
JWT_KEY = os.getenv("JWT_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

FASTAPI_USERS_SECRET = os.getenv("FASTAPI_USERS_SECRET")

ADMIN_PANEL_ENABLED = os.getenv("ADMIN_PANEL_ENABLED")

# pyro
TG_SESSION_STRING = os.getenv("TG_SESSION_STRING")

# google
GOOGLE_CREDENTIALS_FILE_STR = os.getenv("GOOGLE_CREDENTIALS_FILE_STR", "{}")
GOOGLE_CREDENTIALS_JSON = json.loads(GOOGLE_CREDENTIALS_FILE_STR)

MSG_LIMIT = 500
MSG_MIN_DATE = datetime.utcnow() - timedelta(days=31)  # datetime.now(UTC)
PASS_SENIORS_TMP = True
TASK_EXECUTION_TIME_LIMIT = 60 * 5
UNIQUE_FILTER = True
TARGET_CHATS = [-1001328702818,
                -1001049086457,
                -1001154585596,
                -1001292405242,
                -1001650380394,
                -1001850397538,
                -1001164103043,
                ]
TARGET_CHATS_TEST = [-1001328702818,
                     -1001049086457, ]


if __name__ == "__main__":
    print(env_file)