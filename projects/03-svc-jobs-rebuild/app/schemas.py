from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class VersionResponse(BaseModel):
    service: str = "03-svc-jobs-rebuild"
    version: str = "0.1.0"