from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        trace_id = getattr(request.state, "request_id", "unknown")

        if isinstance(exc.detail, dict):
            error_code = str(exc.detail.get("error_code", "HTTP_ERROR"))
            message = str(exc.detail.get("message", "request failed"))
        else:
            error_code = "HTTP_ERROR"
            message = str(exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": error_code,
                "message": message,
                "trace_id": trace_id,
            },
            headers={"X-Request-ID": trace_id},
        )