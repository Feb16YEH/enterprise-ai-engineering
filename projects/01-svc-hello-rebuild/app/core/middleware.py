import json
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request


logger = logging.getLogger("app.requests")
logging.basicConfig(level=logging.INFO)


def add_request_context_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        started_at = time.perf_counter()
        
        response = await call_next(request)

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                }
            )
        )
        return response
