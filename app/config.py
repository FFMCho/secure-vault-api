"""Zentrale Konfiguration aus Umgebungsvariablen."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings – liest aus .env und Umgebungsvariablen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Secure Vault API"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Datenbank
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/secure_vault"

    # JWT
    jwt_secret_key: str = "change-me-in-production-use-secure-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 15

    # S3 / Object Storage
    s3_endpoint_url: str | None = None  # z.B. http://minio:9000 für MinIO
    s3_region: str = "us-east-1"
    s3_bucket: str = "secure-vault"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_presigned_url_expire_seconds: int = 300  # 5 Minuten

    # Limits
    max_file_size_bytes: int = 50 * 1024 * 1024  # 50 MB
    allowed_mime_types: str = "application/pdf,image/jpeg,image/png,image/gif,text/plain,application/zip"


@lru_cache
def get_settings() -> Settings:
    """Gecachte Settings-Instanz."""
    return Settings()
