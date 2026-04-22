from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.models import ReportSpec
from app.routers import reports


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title="svc-catalog-rebuild",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(reports.router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}