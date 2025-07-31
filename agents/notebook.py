# agents/notebook.py

import os
import sys
import threading
import sqlite3
import uvicorn

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Добавляем корень проекта в sys.path для корректного импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Импорт маршрутов
from agents.notebook.auth import router as auth_router
from agents.notebook.views import router as views_router

# Создание FastAPI-приложения
app = FastAPI()

# Настройка статических файлов и шаблонов
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Подключение роутеров
app.include_router(auth_router)
app.include_router(views_router)

def run_notebook(host: str = "127.0.0.1", port: int = 8000):
    """
    Запуск FastAPI-сервера в отдельном потоке.
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    print("[*] Запуск пользовательского интерфейса...")
    thread = threading.Thread(target=run_notebook, daemon=True)
    thread.start()
    thread.join()
