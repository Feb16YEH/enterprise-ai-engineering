import json
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

from sqlmodel import Session

from app.core.config import settings
from app.db.models import Job, JobStatus
from app.db.session import open_session

logger = logging.getLogger("app.jobs")

JobRunner = Callable[[int], None]


def get_job_runner() -> JobRunner:
    return run_job


def run_job(job_id: int) -> None:
    with open_session() as session:
        _run_job_with_session(job_id=job_id, session=session)


def _run_job_with_session(*, job_id: int, session: Session) -> None:
    job = session.get(Job, job_id)
    if job is None:
        logger.error(json.dumps({"event": "job_missing", "job_id": job_id}))
        return
    
    started = time.perf_counter()

    job.status = JobStatus.RUNNING
    job.started_at = datetime.now(UTC)
    session.add(job)
    session.commit()

    logger.info(
        json.dumps(
            {
                "event": "job_started",
                "job_id": job_id,
                "task_type": job.task_type,
            }
        )
    )

    try:
        sleep_seconds = float(job.payload.get("simulate_seconds",
settings.default_job_seconds))
        should_fail = bool(job.payload.get("should_fail", False))

        time.sleep(sleep_seconds)

        if should_fail:
            raise RuntimeError("simulated job failure")
        
        job.status = JobStatus.DONE
        job.result_summary = _build_result_summary(job)
        job.error_message = None

    except Exception as exc: # noqa: BLE001
        job.status = JobStatus.FAILED
        job.result_summary = None
        job.error_message = str(exc)
        logger.exception("job failed", extra={"job_id": job_id})

    finally:
        job.finished_at = datetime.now(UTC)
        job.duration_ms = round((time.perf_counter() - started) * 1000, 2)
        session.add(job)
        session.commit()

        logger.info(
            json.dumps(
                {
                    "event": "job_finished",
                    "job_id": job_id,
                    "status": job.status,
                    "duration_ms": job.duration_ms,
                }
            )
        )


def _build_result_summary(job: Job) -> str:
    if job.task_type == "report_export":
        report_name = job.payload.get("report_name", "unknown_report")
        return f"report_export completed for {report_name}"
    
    if job.task_type == "data_extract":
        source = job.payload.get("source", "unknown_source")
        return f"data_extract completed from {source}"
    
    if job.task_type == "load_table":
        table = job.payload.get("table", "unknown_table")
        return f"load_table completed into {table}"
    
    return f"{job.task_type} completed successfully"