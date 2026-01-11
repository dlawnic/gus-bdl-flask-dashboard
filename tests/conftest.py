import os
import tempfile
import pytest

from app import create_app
from app.extensions import db

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    class TestConfig:
        SECRET_KEY = "test"
        TESTING = True
        WTF_CSRF_ENABLED = False
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        CACHE_DIR = tempfile.mkdtemp()
        CACHE_MAX_AGE_HOURS = 0
        BDL_BASE_URL = "https://bdl.stat.gov.pl/api/v1"
        BDL_CLIENT_ID = ""

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
