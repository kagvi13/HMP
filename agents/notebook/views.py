# agents/notebook/views.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tools.storage import Storage

router = APIRouter()
templates = Jinja2Templates(directory="agents/notebook/templates")
storage = Storage()

DID = "did:example:local-user"  # 🔧 временная заглушка

@router.get("/chat")
def chat_page(request: Request):
    notes = storage.fetchall(
        "SELECT text, timestamp, source FROM notes WHERE hidden=0 AND user_did=? ORDER BY timestamp DESC LIMIT 20",
        (DID,)
    )
    return templates.TemplateResponse("chat.html", {"request": request, "notes": notes})

@router.post("/chat")
def submit_note(request: Request, message: str = Form(...)):
    if message.strip():
        storage.execute(
            "INSERT INTO notes (text, source, user_did) VALUES (?, ?, ?)",
            (message.strip(), "user", DID)
        )
    return RedirectResponse(url="/chat", status_code=303)
