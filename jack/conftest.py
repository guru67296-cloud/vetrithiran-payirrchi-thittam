import os
from pathlib import Path

TEST_DB = Path("test_fitbuddy.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"
os.environ["AI_FALLBACK_ENABLED"] = "true"
os.environ["GEMINI_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
