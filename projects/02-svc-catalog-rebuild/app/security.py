from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_sheme = OAuth2PasswordBearer(tokenUrl="token")

FAKE_USERNAME = "admin"
FAKE_PASSWORD = "password"
FAKE_TOKEN = "catalong-admin-token"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def autherticate_user(username: str, password: str) -> str | None:
    if username == FAKE_USERNAME and password == FAKE_PASSWORD:
        return FAKE_TOKEN
    return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    if token != FAKE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return token