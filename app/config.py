import os
from pathlib import Path

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    DB_PATH = os.getenv("DB_PATH", str(Path("instance") / "app.sqlite3"))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "1") == "1"

    BDL_BASE_URL = os.getenv("BDL_BASE_URL", "https://bdl.stat.gov.pl/api/v1")
    BDL_CLIENT_ID = os.getenv("BDL_CLIENT_ID", "").strip()

    CACHE_DIR = os.getenv("CACHE_DIR", str(Path("instance") / "cache"))
    CACHE_MAX_AGE_HOURS = int(os.getenv("CACHE_MAX_AGE_HOURS", "168"))
