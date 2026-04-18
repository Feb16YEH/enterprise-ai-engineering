from typing import Any

from fastapi import HTTPException, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        error_code = str(detail.get("error_code", f"HTTP_{exc.status_code}"))
        message = str(detail.get("message", "request failed"))
    else:
        error_code = f"HTTP_{exc.status_code}"
        message = str(detail)

    return _error_response(
        status_code=exc.status_code,
        error_code=error_code,
        message=message,
        trace_id=_trace_id(request),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message=_validation_message(exc.errors()),
        trace_id=_trace_id(request),
    )


def _error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    trace_id: str,
) -> JSONResponse:
    payload = ErrorResponse(
        error_code=error_code,
        message=message,
        trace_id=trace_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump()
    )


def _trace_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _validation_message(errors: list[dict[str, Any]]) -> str:
    if not errors:
        return "request validation failed"
    
    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.get("loc", []))
    message = first_error.get("msg", "invalid value")
    return f"{location}: {message}" if location else str(message)



 