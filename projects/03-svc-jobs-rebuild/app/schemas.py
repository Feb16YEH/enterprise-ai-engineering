from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.db.models import JobStatus


class HealthResponse(BaseModel):
    status: str = "ok"


class VersionResponse(BaseModel):
    service: str
    version: str
    build_sha: str
    build_time: str


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    trace_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobCreate(BaseModel):
    task_type: Literal["report_export", "data_extract", "load_table"]
    payload: dict[str, Any] = Field(default_factory=dict)
    simulate_seconds: float | None = Field(dafault=None, ge=0, le=10)
    should_fail: bool = False


class JobAccepted(BaseModel):
    job_id: int
    status: JobStatus
    detail: str


class JobRead(BaseModel):
    id: int
    task_type: str
    submitted_by: str
    status: JobStatus
    payload: dict[str, Any]
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime
    finished_at: datetime | None
    duration_ms: float | None