# agents/notebook.py

import uvicorn
import threading
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from agents.notebook.auth import router as auth_router
from agents.notebook.views import router as views_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="agents/notebook/static"), name="static")
templates = Jinja2Templates(directory="agents/notebook/templates")

app.include_router(auth_router)
app.include_router(views_router)

def run_notebook():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    print("[*] Запуск пользовательского интерфейса...")
    thread = threading.Thread(target=run_notebook, daemon=True)
    thread.start()
