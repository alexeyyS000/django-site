import os

import dotenv

from .settings import *

dotenv_path = os.path.join(os.path.dirname(__file__), ".env.local")

dotenv.load_dotenv(dotenv_path, override=True)

MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT")

DATABASES["default"]["HOST"] = os.environ.get("DB_HOST")

CACHES["default"]["LOCATION"] = "redis://127.0.0.1:6379/1"
