from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://coach:coach@localhost:5432/coach"
    scribe_api_url: str = "http://localhost:8012"
    scribe_api_key: str = "changeme"
    scribe_poll_interval_seconds: int = 60
    file_storage_path: str = "/data/recordings"
    max_upload_size_mb: int = 1000
    api_key: str = "changeme"


settings = Settings()
