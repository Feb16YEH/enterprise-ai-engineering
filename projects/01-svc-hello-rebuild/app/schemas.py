from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"

class VersionResponse(BaseModel):
    service: str
    version: str
    build_sha: str
    build_time: str

class EchoRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=100,
        json_schema_extra={"example": "Hello AI"},
    )


class EchoResponse(BaseModel):
    message: str
    length: int
    request_id: str

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    trace_id: str