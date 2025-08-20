from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Body, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from requests import request, HTTPError
from pathlib import Path
from traffic.TokenManage import TokenManager
from traffic.NotesClient import NotesClient


router = APIRouter(prefix="/user", tags=["User"])
BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse, name="index")
def show_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/auth/register", response_class=HTMLResponse, name="register_page")
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.get("/auth/login", response_class=HTMLResponse, name="login_page")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/auth/register", name="register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...)
    ):
    
    tm = TokenManager(email, password)
    
    try:
        tm.register(name)
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 409:
            resp = templates.TemplateResponse(
                "auth/register.html",
                {"request": request, "error": "E-Mail ist schon vergeben."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
    
    token = tm.get_token()
    resp = RedirectResponse(url=request.url_for("get_notes"), status_code=303)
    resp.set_cookie("access_token", token, httponly=True, samesite="lax")
    
    return resp

@router.post("/auth/login", name="login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    tm = TokenManager(username, password)
    
    try:
        tm.authenticate()
    except:
        return templates.TemplateResponse("auth/login.html", {"request": request})
    
    # httpOnly-Cookie
    token = tm.get_token()
    resp = RedirectResponse(url=request.url_for("get_notes"), status_code=303)
    resp.set_cookie("access_token", token, httponly=True, samesite="lax")
    
    return resp