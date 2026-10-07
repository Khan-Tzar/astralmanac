import pytest

from astralmanac import config, store


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Point the store at a throwaway SQLite file for every test."""
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    # store caches a thread-local connection; clear it so each test is isolated.
    import astralmanac.store as s
    if hasattr(s._local, "conn"):
        s._local.conn.close()
        del s._local.conn
    store.init_db()
    yield
