import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

MINIO_STORAGE_ACCESS_KEY = os.environ.get("MINIO_STORAGE_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = os.environ.get("MINIO_STORAGE_SECRET_KEY")
MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT")

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
DB_HOST = os.environ.get("DB_HOST")

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
