from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    service_name: str = "01-svc-hello-rebuild"
    version: str = "0.1.0"
    build_sha: str = Field(default="local", alias="BUILD_SHA")
    build_time: str = Field(default="unknown", alias="BUILD_TIME")


settings = Settings()