import pytest
from agents.tools.storage import Storage

@pytest.fixture
def storage():
    # Создаём инстанс Storage с временной или тестовой базой
    # Можно настроить, чтобы база была in-memory для быстроты
    return Storage({"db_path": ":memory:"})

def test_add_and_get_journal_entry(storage):
    text = "Первая тестовая запись"
    entry_id = storage.add_journal_entry(text)
    assert isinstance(entry_id, int), "ID записи должен быть числом"

    entry = storage.get_journal_entry(entry_id)
    assert entry is not None, "Запись должна существовать"
    assert entry["text"] == text, "Текст записи должен совпадать"
