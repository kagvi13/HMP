# agents/tests/test_storage.py

import os
import pytest
from agents.tools.storage import Storage

@pytest.fixture
def temp_storage(tmp_path):
    db_path = tmp_path / "test.db"
    storage = Storage(config={"db_path": str(db_path)})
    yield storage
    # автоматически удалится tmp_path

def test_set_and_get(temp_storage):
    temp_storage.set("foo", "bar")
    assert temp_storage.get("foo") == "bar"

def test_delete(temp_storage):
    temp_storage.set("key", "value")
    temp_storage.delete("key")
    assert temp_storage.get("key") is None
