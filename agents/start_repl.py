import sys
import os
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from init import ensure_db_initialized
from tools.storage import Storage

# Проверка инициализации (вернёт config, если всё ОК)
config = ensure_db_initialized()

storage = Storage()

# ⚙️ Включение/отключение компонентов
ENABLE_REPL      = False  # 🧠 repl.py
ENABLE_UI        = True  # 📓 web_ui.py (FastAPI)
ENABLE_MESH      = False  # 🌐 agent_mesh_listener.py
ENABLE_SYNC      = True  # 🔄 peer_sync.py
ENABLE_TRANSPORT = False  # 📡 transporter.py
ENABLE_CONTROL   = False  # 🧭 agent_controller.py
ENABLE_CONTAINER = False  # 🧱 container_agent.py
ENABLE_ETHICS    = False  # 🧠 ethics_guard.py

def start_all():
    threads = []

    if ENABLE_REPL:
        if not storage.is_process_alive("REPL", max_delay=180):
            def repl():
                from repl import start_repl
                start_repl()
            threads.append(threading.Thread(target=repl, name="REPL"))
        else:
           print("REPL уже работает по данным heartbeat.")

    if ENABLE_UI:
        if not storage.is_process_alive("NotebookUI", max_delay=180):
            def ui():
                from web_ui import start_notebook
                start_notebook()
            threads.append(threading.Thread(target=ui, name="NotebookUI"))
        else:
           print("NotebookUI уже работает по данным heartbeat.")

    if ENABLE_MESH:
        if not storage.is_process_alive("MeshListener", max_delay=180):
            def mesh():
                from agent_mesh_listener import start_listener
                start_listener()
            threads.append(threading.Thread(target=mesh, name="MeshListener"))
        else:
           print("MeshListener уже работает по данным heartbeat.")

    if ENABLE_SYNC:
        if not storage.is_process_alive("PeerSync", max_delay=180):
            def sync():
                from peer_sync import start_sync
                start_sync()
            threads.append(threading.Thread(target=sync, name="PeerSync"))
        else:
           print("PeerSync уже работает по данным heartbeat.")

    if ENABLE_TRANSPORT:
        if not storage.is_process_alive("Transporter", max_delay=180):
            def transport():
                from transporter import start_transporter
                start_transporter()
            threads.append(threading.Thread(target=transport, name="Transporter"))
        else:
           print("Transporter уже работает по данным heartbeat.")

    if ENABLE_CONTROL:
        if not storage.is_process_alive("Controller", max_delay=180):
            def control():
                from agent_controller import start_controller
                start_controller()
            threads.append(threading.Thread(target=control, name="Controller"))
        else:
           print("Controller уже работает по данным heartbeat.")

    if ENABLE_CONTAINER:
        if not storage.is_process_alive("ContainerAgent", max_delay=180):
            def container():
                from container_agent import start_container
                start_container()
            threads.append(threading.Thread(target=container, name="ContainerAgent"))
        else:
           print("ContainerAgent уже работает по данным heartbeat.")

    if ENABLE_ETHICS:
        if not storage.is_process_alive("EthicsGuard", max_delay=180):
            def ethics():
                from ethics_guard import start_ethics_guard
                start_ethics_guard()
            threads.append(threading.Thread(target=ethics, name="EthicsGuard"))
        else:
           print("EthicsGuard уже работает по данным heartbeat.")

    # Запуск потоков
    for thread in threads:
        try:
            thread.start()
            print(f"[✔] Поток {thread.name} запущен.")
        except Exception as e:
            print(f"[⚠️] Ошибка запуска потока {thread.name}: {e}")

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    print("[*] Инициализация завершена. Запуск потоков...")
    start_all()
