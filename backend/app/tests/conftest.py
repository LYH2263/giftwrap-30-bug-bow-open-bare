import pytest
from app import config, db, seed

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """每个用例独立 sqlite 库。"""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", db_file)
    monkeypatch.setattr(config, "DB_PATH", db_file)
    seed.init_db()
    yield db_file
