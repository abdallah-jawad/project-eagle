from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    client_id: str
    created_at: datetime
    last_login: Optional[datetime] = None

class UserInDB(User):
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str
    client_id: str

class TokenData(BaseModel):
    email: Optional[str] = None
    client_id: Optional[str] = None 