from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str
    
class NotesOut(BaseModel):
    id: int
    title: str
    text: str
    created: datetime
    created_by: int
    category: int
    class Config:
        from_attributes = True
        
class NoteCreate(BaseModel):
    title: str
    text: str
    category: str | None = None