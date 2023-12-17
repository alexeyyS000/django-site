import os

import dotenv

from .settings import *

dotenv_path = os.path.join(os.path.dirname(__file__), ".env.local")

dotenv.load_dotenv(dotenv_path, override=True)

MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT")

DATABASES["default"]["HOST"] = os.environ.get("DB_HOST")

CACHES["default"]["LOCATION"] = "redis://127.0.0.1:6379/1"

MINIO_STORAGE_MEDIA_URL = "http://localhost:9000/local-media/"

CELERY_BROKER_URL = "redis://localhost:6379/2"
CELERY_RESULT_BACKEND = "redis://localhost:6379/3"
