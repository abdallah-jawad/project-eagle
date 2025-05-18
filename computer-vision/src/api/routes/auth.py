from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/authorize")
async def authorize(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    Authorize user and return JWT token
    """
    # TODO: Implement actual authentication logic
    return {"access_token": "dummy_token", "token_type": "bearer"}

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Get current user information
    """
    # TODO: Implement user info retrieval
    return {"username": "dummy_user"} 