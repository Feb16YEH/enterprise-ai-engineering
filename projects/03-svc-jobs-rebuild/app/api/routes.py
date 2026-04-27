from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status, Query, HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.schemas import (
    HealthResponse,
    VersionResponse,
    TokenResponse,
    JobAccepted,
    JobCreate,
    JobRead,
)
from app.shared.auth import User, authenticate_user, get_current_user
from app.db.models import Job, JobStatus
from app.db.session import get_session
from app.services.jobs import JobRunner, get_job_runner

router = APIRouter()
TokenUserDep = Annotated[User, Depends(authenticate_user)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
JobRunnerDep = Annotated[JobRunner, Depends(get_job_runner)]
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
    background_tasks: BackgroundTasks,
    session: SessionDep,
    current_user: CurrentUserDep,
    job_runner: JobRunnerDep,
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
    
    background_tasks.add_task(job_runner, job.id)
    
    return JobAccepted(
        job_id=job.id,
        status=job.status,
        detail="job accepted for background execution",
    )


@router.get("/jobs", response_model=list[JobRead])
async def list_jobs(
    session: SessionDep,
    current_user: CurrentUserDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Job]:
    statement = (
        select(Job)
        .where(Job.submitted_by == current_user.username)
        .order_by(Job.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement).all())



@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(
    job_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> Job:
    job = _get_job_or_404(session=session, job_id=job_id)

    if job.submitted_by != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "JOB_FORBIDDEN",
                "message": "you can only read jobs submitted by yourself",
            },
        )
    
    return job


def _get_job_or_404(*, session: Session, job_id: int) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "JOB_NOT_FOUND",
                "message": f"job {job_id} was not found",
            },
        )
    
    return job