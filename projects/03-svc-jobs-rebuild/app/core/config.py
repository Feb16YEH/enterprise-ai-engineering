from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str ="03-svc-jobs-rebuild"
    version: str = "0.1.0"
    build_sha: str = "local"
    build_time: str = "unknown"

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()