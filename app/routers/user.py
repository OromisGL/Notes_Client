from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Body, Form 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from schemas.schemas import UserCreate, UserLogin, TokenOut,UserOut, NotesOut, NoteCreate
from traffic.TokenManage import TokenManager
from traffic.NotesClient import NotesClient


router = APIRouter(prefix="/user", tags=["User"])
BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
):
    tm = TokenManager(email, password)
    try:
        new_user = tm.register(name)
    except Exception as e:
        # z. B. E-Mail existiert schon
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    # Erfolg – z. B. Bestätigungsseite rendern
    return templates.TemplateResponse(
        "success.html",
        {"request": request, "user": new_user},
        status_code=status.HTTP_201_CREATED,
    )

@router.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    tm = TokenManager(form_data.username, form_data.password)
    
    try:
        tm.authenticate()
    except Exception:
        raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten.")
    
    # httpOnly-Cookie
    token = tm.get_token()
    response.set_cookie("access_token", token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/notes")
def get_notes(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    nc = NotesClient(token=token) 
    return nc.list_all()

@router.post("/notes", response_model=NotesOut)
def post_notes(request: Request, note: NoteCreate):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    nc = NotesClient(token=token)
    
    try:
        created = nc.post(title=note.title, text=note.text, category=note.category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=(e))

    return created