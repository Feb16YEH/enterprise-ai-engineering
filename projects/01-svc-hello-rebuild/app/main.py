from fastapi import FastAPI

from app.api.routes import router
from app.core.errors import register_exception_handlers
from app.core.middleware import add_request_context_middleware


def create_app() -> FastAPI:
    app = FastAPI(title="01-svc-hello-rebuild")

    add_request_context_middleware(app)
    register_exception_handlers(app)
    app.include_router(router)

    return app


app = create_app()