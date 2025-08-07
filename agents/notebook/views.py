# agents/notebook/views.py

import re
import bleach

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from tools.storage import Storage

router = APIRouter()
templates = Jinja2Templates(directory="notebook/templates")
storage = Storage()

allowed_tags = ['b', 'i', 's', 'u', 'a', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'table', 'caption', 'tr', 'th', 'td', 'code', 'pre', 'blockquote', 'br', 'hr']
allowed_attributes = {
    'a': ['href', 'title']
}

# Очистка сообщений
def sanitize_html(text: str) -> str:
    # 1. Сначала очищаем HTML
    cleaned = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    # 2. Заменяем 3 и более <br> подряд на ровно два
    cleaned = re.sub(r'(<br\s*/?>\s*){3,}', '<br><br>', cleaned, flags=re.IGNORECASE)

    return cleaned

@router.get("/chat")
def chat_page(request: Request):
    did = request.session.get("did")
    username = request.session.get("username")
    if not did:
        return RedirectResponse("/login", status_code=303)

    notes = storage.fetchall(
        "SELECT text, timestamp, source FROM notes WHERE hidden=0 AND user_did=? ORDER BY timestamp DESC LIMIT 20",
        (did,)
    )
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "notes": notes,
        "username": username
    })

@router.post("/chat")
def submit_note(request: Request, message: str = Form(...)):
    did = request.session.get("did", "anon")
    if message.strip():
        storage.write_note(
            content=message.strip(),
            user_did=did,
            source="user"
        )
    return RedirectResponse(url="/chat", status_code=303)

@router.get("/messages")
def show_messages(request: Request, only_personal: bool = False):
    did = request.session.get("did")
    username = request.session.get("username")
    if not did:
        return RedirectResponse("/login", status_code=303)

    messages = storage.get_notes(
        limit=50,
        user_did=did,
        only_personal=only_personal
    )
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "messages": messages,
        "only_personal": only_personal,
        "username": username
    })

@router.post("/messages")
def post_message(
    request: Request,
    text: str = Form(...),
    hidden: str = Form(default="false")
):
    did = request.session.get("did", "anon")
    is_hidden = 1 if hidden.lower() == "true" else 0

    # Проверка на бан
    if storage.is_banned(did):
        return HTMLResponse(content="Вы забанены и не можете отправлять сообщения.", status_code=403)

    if text.strip():
        storage.write_note(
            content=sanitize_html(text.strip()),
            user_did=did,
            source="user",
            hidden=is_hidden
        )
    return RedirectResponse(url="/messages", status_code=303)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, mail: str = Form(...), password: str = Form(...)):
    if storage.authenticate_user(mail, password):
        user_info = storage.get_user_info(mail)
        request.session["username"] = user_info["username"]
        request.session["did"] = user_info["did"]
        return RedirectResponse("/messages", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Неверный email или пароль"
    })

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    mail: str = Form(...),
    password: str = Form(...)
):
    if storage.register_user(username, mail, password):
        user_info = storage.get_user_info(mail)
        request.session["username"] = user_info["username"]
        request.session["did"] = user_info["did"]
        return RedirectResponse("/messages", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": "Пользователь с таким email уже существует"
    })

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
