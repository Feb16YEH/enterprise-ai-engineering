from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.schemas import HealthResponse, VersionResponse, TokenResponse
from app.shared.auth import User, authenticate_user, get_current_user

router = APIRouter()
TokenUserDep = Annotated[User, Depends(authenticate_user)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse(
        service=settings.service_name,
        version=settings.version,
        build_sha=settings.build_sha,
        build_time=settings.build_time,
    )


@router.post("/token", response_model=TokenResponse)
async def token(user: TokenUserDep) -> TokenResponse:
    return TokenResponse(access_token=user.token)


@router.get("/me")
async def me(current_user: CurrentUserDep) -> dict[str, str]:
    return {"username": current_user.username}