from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


class User(BaseModel):
    username: str
    token: str


USERS = {
    "alice": {"password": "secret", "token": "token-alice"},
    "bob": {"password": "secret", "token": "token-bob"},
}

TOKENS = {
    user_data["token"]: username
    for username, user_data in USERS.items()
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def authenticate_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> User:
    user_data = USERS.get(form_data.username)
    if user_data is None or user_data["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_CREDENTIALS",
                "message": "invalid username or password",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(username=form_data.username, token=user_data["token"])


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    username = TOKENS.get(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_TOKEN",
                "message": "missing or invalid beared token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(username=username, token=token)
