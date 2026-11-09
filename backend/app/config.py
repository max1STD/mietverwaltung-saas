"""Application configuration via Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me"  # noqa: S105 - dev placeholder, overridden in prod

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://mv:change-me@db:5432/mietverwaltung"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    JWT_SECRET: str = "change-me"  # noqa: S105 - dev placeholder, overridden in prod
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # KI (Ollama Cloud)
    OLLAMA_API_URL: str = "https://ollama.com/v1"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL_DEFAULT: str = "glm-5.2"
    OLLAMA_MODEL_COMPLEX: str = "kimi-k2.6"

    # E-Mail
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@mietverwaltung.de"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # GeoIP
    MAXMIND_LICENSE_KEY: str = ""
    GEOIP_DB_PATH: str = "/app/data/GeoLite2-Country.mmdb"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
