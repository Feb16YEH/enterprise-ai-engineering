from pydantic import BaseModel


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
