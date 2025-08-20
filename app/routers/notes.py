from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Body, Form 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from schemas.schemas import NotesOut, NoteCreate
from traffic.TokenManage import TokenManager
from traffic.NotesClient import NotesClient
from pathlib import Path

router = APIRouter(prefix="/content", tags=["Content"])
BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/note", response_class=HTMLResponse, name="get_notes")
def get_notes(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    notes = NotesClient(token).list_all()[::-1]
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes
        })

@router.post("/delete", name="delete_ui")
def delete_note(request: Request, note_id: int = Form(...)):
    token = request.cookies.get("access_token")
    data = NotesClient(token)
    
    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    data.delete(note_id)
    
    notes = data.list_all()[::-1]
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes
        })

@router.post("/post", name="create_note")
def post_notes(request: Request, title: str = Form(...), text: str = Form(...), category: str = Form(...)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    nc = NotesClient(token)
    
    try:
        nc.post(title, text, category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=(e))
    
    notes = NotesClient(token).list_all()[::-1]
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes
        })