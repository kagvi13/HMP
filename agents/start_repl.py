import sys
import os
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.init import ensure_db_initialized

# Проверка инициализации (вернёт config, если всё ОК)
config = ensure_db_initialized()

# ⚙️ Включение/отключение компонентов
ENABLE_REPL      = False  # 🧠 repl.py
ENABLE_UI        = True  # 📓 notebook.py (FastAPI)
ENABLE_MESH      = False  # 🌐 agent_mesh_listener.py
ENABLE_SYNC      = False  # 🔄 peer_sync.py
ENABLE_TRANSPORT = False  # 📡 transporter.py
ENABLE_CONTROL   = False  # 🧭 agent_controller.py
ENABLE_CONTAINER = False  # 🧱 container_agent.py
ENABLE_ETHICS    = False  # 🧠 ethics_guard.py

def start_all():
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

    if ENABLE_TRANSPORT:
        def transport():
            from agents.transporter import start_transporter
            start_transporter()
        threads.append(threading.Thread(target=transport, name="Transporter"))

    if ENABLE_CONTROL:
        def control():
            from agents.agent_controller import start_controller
            start_controller()
        threads.append(threading.Thread(target=control, name="Controller"))

    if ENABLE_CONTAINER:
        def container():
            from agents.container_agent import start_container
            start_container()
        threads.append(threading.Thread(target=container, name="ContainerAgent"))

    if ENABLE_ETHICS:
        def ethics():
            from agents.ethics_guard import start_ethics_guard
            start_ethics_guard()
        threads.append(threading.Thread(target=ethics, name="EthicsGuard"))

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
