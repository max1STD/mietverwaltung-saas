"""Application lifespan: startup and shutdown events."""
import structlog
from fastapi import FastAPI

from app.config import settings

logger = structlog.get_logger()


async def startup(app: FastAPI) -> None:
    logger.info("app.starting", environment=settings.ENVIRONMENT)


async def shutdown(app: FastAPI) -> None:
    logger.info("app.stopping")
