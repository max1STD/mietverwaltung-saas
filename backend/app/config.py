"""Application configuration via Pydantic Settings.

Lädt Einstellungen aus der .env-Datei im Projekt-Root (../.env relativ zum backend/).
Alle Secrets werden in Production über SOPS+age oder Systemd-EnvironmentFiles gesetzt.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Zentrale Konfiguration — aus .env geladen, mit sicheren Defaults."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me"  # noqa: S105

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://mv:change-me@127.0.0.1:5432/mietverwaltung"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://mv:change-me@127.0.0.1:5432/mietverwaltung"

    # ── Redis ──
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # ── JWT ──
    JWT_SECRET: str = "change-me"  # noqa: S105
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # ── KI (Ollama Cloud) ──
    OLLAMA_API_URL: str = "https://ollama.com/v1"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL_DEFAULT: str = "glm-5.2"
    OLLAMA_MODEL_COMPLEX: str = "kimi-k2.6"

    # ── E-Mail (Resend) ──
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@mietverwaltung.de"

    # ── Stripe ──
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # ── GeoIP (MaxMind) ──
    MAXMIND_LICENSE_KEY: str = ""
    GEOIP_DB_PATH: str = "/app/data/GeoLite2-Country.mmdb"

    # ── Encryption (AES-256-GCM) ──
    DB_ENCRYPTION_KEY: str = ""  # Base64-encoded 32-byte key

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
