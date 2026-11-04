"""FastAPI application factory for MietVerwaltung SaaS."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.lifespan import startup, shutdown


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    yield
    await shutdown(app)


app = FastAPI(
    title="MietVerwaltung SaaS",
    description="KI-gestützte Mietverwaltung für private Kleinvermieter in DACH",
    version="0.1.0",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# Routes (imported after app creation to avoid circular imports)
from app.routes import auth, health  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
