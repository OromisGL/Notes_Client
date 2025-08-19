from fastapi import FastAPI, APIRouter
from routers import user, notes

app = FastAPI()
router = APIRouter()

app.include_router(user.router)
app.include_router(notes.router)