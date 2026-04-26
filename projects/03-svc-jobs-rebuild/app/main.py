from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="03-svc-jobs-rebuild",
        version="0.1.0",
        description="Background job API rebuild step by step.",
    )
    app.include_router(router)
    return app


app = create_app()