# agents/notebook/views.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from tools.storage import Storage

router = APIRouter()
templates = Jinja2Templates(directory="notebook/templates")
storage = Storage()

DID = "did:example:local-user"  # временно

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

@router.get("/messages")
def show_messages(request: Request):
    messages = storage.get_notes(limit=50)
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "messages": messages
    })

@router.post("/messages")
def post_message(
    request: Request,
    text: str = Form(...),
    user_did: str = Form(default="anon")
):
    storage.write_note(
        content=text,
        user_did=user_did,
        source="user"
    )
    return RedirectResponse(url="/messages", status_code=303)
