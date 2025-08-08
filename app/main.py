from fastapi import FastAPI, APIRouter
from routers import user

app = FastAPI()
router = APIRouter()

app.include_router(user.router)