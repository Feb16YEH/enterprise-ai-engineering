from fastapi import APIRouter

from app.schemas import HealthResponse, VersionResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    return VersionResponse()
