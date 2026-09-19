"""Centralized configuration, read from environment variables.
No secrets are hardcoded — see .env.example at the project root."""
import os


class Settings:
    APP_NAME: str = "ClimateGuard AI"
    APP_VERSION: str = "0.1.0-phase1"
    ENV: str = os.getenv("ENV", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./climateguard.db")
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
