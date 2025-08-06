# agents/notebook/views.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from tools.storage import Storage
from passlib.hash import bcrypt
from fastapi import FastAPI

router = APIRouter()
templates = Jinja2Templates(directory="notebook/templates")
storage = Storage()

@router.get("/chat")
def chat_page(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=303)

    notes = storage.fetchall(
        "SELECT text, timestamp, source FROM notes WHERE hidden=0 AND user_did=? ORDER BY timestamp DESC LIMIT 20",
        (username,)
    )
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "notes": notes,
        "username": username
    })

@router.post("/chat")
def submit_note(request: Request, message: str = Form(...)):
    username = request.session.get("user", "anon")  # Можно вернуть anon, если не залогинен
    if message.strip():
        storage.execute(
            "INSERT INTO notes (text, source, user_did) VALUES (?, ?, ?)",
            (message.strip(), "user", username)
        )
    return RedirectResponse(url="/chat", status_code=303)

@router.get("/messages")
def show_messages(request: Request, only_personal: bool = False):
    username = request.session.get("user")
    if not username:
        return RedirectResponse("/login", status_code=303)

    is_operator = False  # Пока не реализовано
    messages = storage.get_notes(
        limit=50,
        user_did=username,
        is_operator=is_operator,
        only_personal=only_personal
    )
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "messages": messages,
        "only_personal": only_personal,
        "username": username  # 👈 вот это
    })

@router.post("/messages")
def post_message(
    request: Request,
    text: str = Form(...),
    user_did: str = Form(default="anon"),
    hidden: str = Form(default=None)
):
    is_hidden = 1 if hidden else 0

    storage.write_note(
        content=text,
        user_did=user_did,
        source="user",
        hidden=is_hidden
    )
    return RedirectResponse(url="/messages", status_code=303)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if storage.authenticate_user(username, password):
        request.session["user"] = username
        return RedirectResponse("/chat", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Неверный логин или пароль"
    })

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if storage.register_user(username, password):
        request.session["user"] = username
        return RedirectResponse("/chat", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": "Пользователь уже существует"
    })

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
