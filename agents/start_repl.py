# agents/start_repl.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
from agents.init import ensure_db_initialized

# Проверка инициализации (вернёт config, если всё ОК)
config = ensure_db_initialized()

# ⚙️ Включение/отключение компонентов
# True | False
ENABLE_REPL = False
ENABLE_UI = True
ENABLE_MESH = False
ENABLE_SYNC = False

def start_all():
    """
    Стартует все ключевые компоненты агента в отдельных потоках.
    """
    threads = []

    if ENABLE_REPL:
        def repl():
            from agents.repl import start_repl
            start_repl()
        threads.append(threading.Thread(target=repl, name="REPL"))

    if ENABLE_UI:
        def ui():
            from agents.notebook import start_notebook
            start_notebook()
        threads.append(threading.Thread(target=ui, name="NotebookUI"))

    if ENABLE_MESH:
        def mesh():
            from agents.agent_mesh_listener import start_listener
            start_listener()
        threads.append(threading.Thread(target=mesh, name="MeshListener"))

    if ENABLE_SYNC:
        def sync():
            from agents.peer_sync import start_sync
            start_sync()
        threads.append(threading.Thread(target=sync, name="PeerSync"))

    # Запуск потоков
    for thread in threads:
        try:
            thread.start()
            print(f"[✔] Поток {thread.name} запущен.")
        except Exception as e:
            print(f"[⚠️] Ошибка запуска потока {thread.name}: {e}")

    # Блокирующее ожидание завершения
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    print("[*] Инициализация завершена. Запуск потоков...")
    start_all()
