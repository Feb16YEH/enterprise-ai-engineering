# 03-svc-jobs-rebuild

A FasiAPI practice service for background job submission and
status tracking.

This servive simulates report export, data extraction, and table
loading jobs. It demonstrates a minimal backend workflow:

```test
POST /jobs
-> create a PENDING job
-> return 202 Accepted immidiately
-> run work in FastAPI BackgroundTasks
-> update status to RUNNING
-> finish as DONE or FAILED
->expose status and logs through query APIs
```

## Features

- FastAPI route modularizaiton with APIRouter
- Ttyped request and response models with Pydantic
- SQLite persistence with SQLModel
- Bearer token autherization for protect job APIs
- Jobs status machine: PENDING -> RUNNING -> DONE / FAILED
- Request ID middleware with X-Request-ID
- Unified error response for HTTPException
-Background task execution with status, duration, result, and error tracking
- Pytest integration tests

## API

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /health | No | Health check|
| GET | /version | No | Service version |
| POST | /token | No | Exchange username/password for a teaching token |
| PSOT | /jobs | Yes | Submit a background job |
| GET | /jobs | Yes | Query current user's jobs |
| GET | /jobs/{job_id} | Yes | Get one job by ID |

## Local Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

## Authentication

Teaching users:
| Username | Password | Token |
|---|---|---|
| alice | secret | token-alice |
| bob | serect | token-bob |

Get a token:

curl -X POST http://localhost:8000/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=alice&password=secret'

Use it:

curl -H "Authorization: Bearer token-alice" http://localhost:8000/jobs

## Submit a Job
curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer token-alice" \
  -H 'Content-Type: application/json' \
  -d '{
    "task_type": "report_export",
    "payload": {
        "report_name": "daily_sales"
    },
    "simualte_seconds": 1,
    "should_fail": "false"
  }

Response:
  {
    "job_id": 1,
    "status": "PENDING",
    "detail": "job accepted for background execution"
  }

Query:

curl -H "Authorization: Bearer token-alice" http:localhost:8000/jobs/1

## Simulate Failure

curl -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer token-alice" \
  -H 'Content-Type: application/json' \
  -d '{
    "task_type": "data_extract",
    "payload": {
        "source": "warehouse.fact_sales"
    },
    "simulate_seconds": 1,
    "should_fail": true
  }'

  Excepected final state:
  {
    "status": "FAILED",
    "error_message": "simulate job failure"
  }

## Error Response

HTTPException response use this shape:

{
    "error_code": "JOB_NOT_FOUND",
    "message": "job 999 was not found",
    "trace_id": "same value as X-Request-ID"
}

## BackgroundTasks Notes

FastAPI BackgroundTasks is useful for this practice stage because
it let the request return quickly while lightweight work countinues
after the response.

It is not a distrubuted queue:

- Tasks run in the same application process.
- A process crash or restart can interrupt running work.
- Multi-woker deployments do not share an in-process task queue.
- It does not provide durable retries, scheduling, ackowledgements, concurrency control, or centralized monitoring.

For production-grade long-running jobs, use a real queue and worker
system such as Redis/RQ, Celery, Arq, RabbitMQ, or Kafka-based workers.

## Test and Lint

ruff check .
pytest