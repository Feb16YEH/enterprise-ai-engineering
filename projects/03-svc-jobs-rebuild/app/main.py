from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.errors import register_exception_handlers
from app.core.middleware import add_request_context_middleware
from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    del app
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="03-svc-jobs-rebuild",
        version="0.1.0",
        description="Background job API rebuild step by step.",
        lifespan=lifespan,
    )

    add_request_context_middleware(app)
    register_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()