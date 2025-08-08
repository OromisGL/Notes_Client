from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from schemas.schemas import UserCreate, UserLogin, TokenOut,UserOut, NotesOut, NoteCreate
from traffic.TokenManage import TokenManager
from traffic.NotesClient import NotesClient

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register", response_model=UserOut)
def register_user(request: Request, data: UserCreate):
    tm = TokenManager(data.email, data.password)
    
    try:
        new_user = tm.register(data.name)
    except Exception as e:
        # z.B. 400 wenn E-Mail schon existiert
        raise HTTPException(status_code=400, detail=str(e))
    return new_user

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