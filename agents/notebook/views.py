from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from tools.storage import Storage

router = APIRouter()
templates = Jinja2Templates(directory="notebook/templates")
storage = Storage()

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

    is_operator = False  # Пока не реализовано
    messages = storage.get_notes(
        limit=50,
        user_did=did,
        is_operator=is_operator,
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
    hidden: str = Form(default=None)
):
    did = request.session.get("did", "anon")
    is_hidden = 1 if hidden else 0

    storage.write_note(
        content=text,
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
