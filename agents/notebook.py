# agent/notebook.py

import os
import sys
import threading
import uvicorn
import asyncio

process_name = os.path.splitext(os.path.basename(__file__))[0]

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from agents.notebook.auth import router as auth_router
from agents.notebook.views import router as notebook_router
from agents.storage import storage

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "notebook/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "notebook/templates"))

app.include_router(auth_router)
app.include_router(notebook_router)

@app.on_event("startup")
async def start_heartbeat():
    asyncio.create_task(heartbeat_loop())

async def heartbeat_loop():
    while True:
        storage.update_heartbeat(process_name)
        if storage.check_stop_flag(process_name):
            print("⛔ Получен сигнал остановки.")
            break
        await asyncio.sleep(60)

def run_notebook(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    print("[*] Запуск пользовательского интерфейса...")
    run_notebook()
