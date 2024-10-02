import logging

from dotenv import load_dotenv, find_dotenv
import os


# load from .env; относительно config.py
env_file = find_dotenv(".env")
env = load_dotenv(env_file)
if not env:
    logging.critical("!!! no .env file")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# for testing
TEST_DB_HOST = os.getenv("TEST_DB_HOST")
TEST_DB_PORT = os.getenv("TEST_DB_PORT")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASS = os.getenv("TEST_DB_PASS")
TEST_DB_URL = os.getenv("TEST_DB_URL")

JWT_KEY = os.getenv("JWT_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

MODE = os.getenv("MODE")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
if TEST_DB_HOST:
    TEST_DB_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"


# pyro
TG_SESSION_STRING = os.getenv("TG_SESSION_STRING")

if __name__ == "__main__":
    print(env_file)
    print(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

