import os

DB_PATH = os.getenv("SHORT_URLS_DB", "./short_urls.db")
BASE_URL = os.getenv("SHORT_URLS_DOMAIN", "http://localhost:9000/")
