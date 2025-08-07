# agent/web_ui.py

import os
import sys
import threading
import uvicorn
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
process_name = os.path.splitext(os.path.basename(__file__))[0]

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from agents.notebook.views import router as notebook_router
from tools.storage import Storage

storage = Storage()
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="очень_секретный_ключ")


app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "notebook/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "notebook/templates"))

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

def start_notebook():
    ui_port = int(storage.get_config_value("ui_port", 8000))
    print(f"[*] Запуск веб-интерфейса на порту {ui_port}")
    uvicorn.run(app, host="127.0.0.1", port=ui_port)

if __name__ == "__main__":
    print("[*] Запуск пользовательского интерфейса...")
    run_notebook()
