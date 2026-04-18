from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.schemas import EchoRequest, EchoResponse, HealthResponse, VersionResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(
        service=settings.service_name,
        version=settings.version,
        build_sha=settings.build_sha,
        build_time= settings.build_time,
    )


@router.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest, request: Request) -> EchoResponse:
    if payload.message == "error":
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "ECHO_BAD_MESSAGE",
                "message": "message cannot be error",
            },
        )
    
    return EchoResponse(
        message=payload.message,
        length=len(payload.message),
        request_id=request.state.request_id,
    )