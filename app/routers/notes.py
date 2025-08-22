from fastapi import APIRouter, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from traffic.NotesClient import NotesClient
from pathlib import Path
from requests import HTTPError

router = APIRouter(prefix="/content", tags=["Content"])
BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/note", name="get_notes")
def get_notes(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Bitte anmelden oder Registrieren."},
            status_code=401)
    
    req = NotesClient(token)
    
    try:
        notes = req.list_all()[::-1]
        categories = req.list_all_cat()
    except HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403):
            resp = templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Sitzung Abgelaufen. Bitte erneut anmelden."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
        
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes,
            "categories": categories
        })

@router.post("/delete", name="delete_ui")
def delete_note(request: Request, note_id: int = Form(...)):
    token = request.cookies.get("access_token")
    
    if not token:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Bitte anmelden oder Registrieren."},
            status_code=401)
    
    data = NotesClient(token)
    try:
        data.delete(note_id)
        notes = data.list_all()[::-1]
    except HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403):
            resp = templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Sitzung Abgelaufen. Bitte erneut anmelden."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes
        })

@router.get("/edit", name="edit_ui")
def register_page(request: Request, note_id: int = Query(...)):
    token = request.cookies.get("access_token")
    
    if not token:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Bitte anmelden oder Registrieren."},
            status_code=401)
    
    try:
        data = NotesClient(token)
        result = data.get_note(note_id)
        categories = data.list_all_cat()
    except HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403):
            resp = templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Sitzung Abgelaufen. Bitte erneut anmelden."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
    
    return templates.TemplateResponse(
        "content/update.html", 
        {"request": request, "data": result, "categories": categories})

@router.post("/update", name="update_ui")
def update(
        request: Request,
        note_id: int = Form(...),
        title: str = Form(...),
        text: str = Form(...),
        category: str = Form(...)):

    token = request.cookies.get("access_token")
    
    if not token:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Bitte anmelden oder Registrieren."},
            status_code=401)
        
    nc = NotesClient(token)
    
    try:
        nc.updater(note_id, title, text, category)
        notes = nc.list_all()[::-1]
        categories = nc.list_all_cat()
    except HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403):
            resp = templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Sitzung Abgelaufen. Bitte erneut anmelden."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes,
            "categories": categories
        })

@router.post("/post", name="create_note")
def post_notes(
        request: Request, 
        title: str = Form(...), 
        text: str = Form(...), 
        category: str = Form(...)
        ):
    token = request.cookies.get("access_token")
    
    if len(text) < 1:
        resp = RedirectResponse(url=request.url_for("get_notes"), status_code=303)
        resp.set_cookie("access_token", token, httponly=True, samesite="lax")
        return resp
    
    if not token:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Bitte anmelden oder Registrieren."},
            status_code=401)
        
    nc = NotesClient(token)
    
    try:
        nc.post(title, text, category)
        notes = NotesClient(token).list_all()[::-1]
    except HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403):
            resp = templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Sitzung Abgelaufen. Bitte erneut anmelden."},
                status_code=401)
            resp.delete_cookie("access_token")
            return resp
        raise
    
    return templates.TemplateResponse(
        "content/note.html", {
            "request": request,
            "notes": notes
        })