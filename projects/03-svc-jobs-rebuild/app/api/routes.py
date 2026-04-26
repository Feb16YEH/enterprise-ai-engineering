from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.config import settings
from app.schemas import (
    HealthResponse,
    VersionResponse,
    TokenResponse,
    JobAccepted,
    JobCreate,
)
from app.shared.auth import User, authenticate_user, get_current_user
from app.db.models import Job, JobStatus
from app.db.session import get_session

router = APIRouter()
TokenUserDep = Annotated[User, Depends(authenticate_user)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]


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


@router.post(
    "/jobs",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_job(
    payload: JobCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> JobAccepted:
    job = Job(
        task_type=payload.task_type,
        submitted_by=current_user.username,
        status=JobStatus.PENDING,
        payload={
            **payload.payload,
            "simulate_seconds": payload.simulate_seconds
            if payload.simulate_seconds is not None
            else settings.default_job_seconds,
            "should_fail": payload.should_fail,
        },
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    if job.id is None:
        raise RuntimeError("job id was not generated")
    
    return JobAccepted(
        job_id=job.id,
        status=job.status,
        detail="job accepted for background execution",
    )
