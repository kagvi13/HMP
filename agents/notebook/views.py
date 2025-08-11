# agents/notebook/views.py

import re
import bleach
import uuid
import json

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from starlette.status import HTTP_303_SEE_OTHER
from typing import List
from tools.storage import Storage

router = APIRouter()
templates = Jinja2Templates(directory="notebook/templates")
storage = Storage()

allowed_tags = ['b', 'i', 's', 'u', 'a', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'table', 'caption', 'tr', 'th', 'td', 'code', 'pre', 'blockquote', 'br', 'hr']
allowed_attributes = {
    'a': ['href', 'title']
}

# Обработка даты и времени
def format_timestamp(value):
    try:
        dt = datetime.fromtimestamp(float(value))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)

templates.env.filters['format_timestamp'] = format_timestamp

# Очистка сообщений
def sanitize_html(text: str) -> str:
    # 1. Сначала очищаем HTML
    cleaned = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    # 2. Заменяем 3 и более <br> подряд на ровно два
    cleaned = re.sub(r'(<br\s*/?>\s*){3,}', '<br><br>', cleaned, flags=re.IGNORECASE)

    return cleaned

# Обработка упоминаний и хештегов
def extract_mentions_and_hashtags(text: str):
    # Пример: упоминания в виде @did:example:123 или @username
    mentions = re.findall(r'@([\w:.-]+)', text)

    # Пример: хештеги в виде #tag
    hashtags = re.findall(r'#(\w+)', text)

    return mentions, hashtags

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
async def post_message(
    request: Request,
    text: str = Form(...),
    code: str = Form(None),
    hidden: str = Form(default="false"),
    binary_files: List[UploadFile] = File(default=[])
):
    did = request.session.get("did", "anon")
    is_hidden = 1 if hidden.lower() == "true" else 0

    if storage.is_banned(did):
        return HTMLResponse(content="Вы забанены и не можете отправлять сообщения.", status_code=403)

    if text.strip() or code or binary_files:
        # Очистка текста
        safe_text = sanitize_html(text.strip()) if text else ""

        # Извлечение mentions, hashtags
        mentions, hashtags = extract_mentions_and_hashtags(safe_text)

        # Сохраняем сообщение и получаем message_id
        message_id = storage.write_note_returning_id(
            content=safe_text,
            user_did=did,
            source="user",
            hidden=is_hidden,
            code=code.strip() if code else None,
            mentions=json.dumps(mentions, ensure_ascii=False),
            hashtags=json.dumps(hashtags, ensure_ascii=False)
        )

        # Сохраняем файлы
        for upload in binary_files:
            data = await upload.read()
            if data:
                storage.save_attachment(
                    message_id=message_id,
                    filename=upload.filename,
                    mime_type=upload.content_type,
                    content=data
                )

    return RedirectResponse(url="/messages", status_code=303)

@router.get("/download/{file_id}")
def download_file(file_id: int):
    file = storage.get_attachment_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    return StreamingResponse(
        iter([file["binary"]]),
        media_type=file["mime_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{file["filename"]}"'
        }
    )

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
