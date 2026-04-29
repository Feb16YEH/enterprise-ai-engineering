from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class JobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_type: str
    submitted_by: str
    status: JobStatus = Field(default=JobStatus.PENDING)

    payload: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )

    result_summary: str | None = None
    error_message: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: float | None = None
