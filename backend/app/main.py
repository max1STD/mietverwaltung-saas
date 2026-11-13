"""FastAPI application factory for MietVerwaltung SaaS."""
from contextlib import asynccontextmanager
import secrets

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.lifespan import shutdown, startup


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


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Setzt CSP-Nonce, CSRF-Cookie und sichere Response-Header."""
    nonce = secrets.token_urlsafe(16)
    request.state.nonce = nonce

    response = await call_next(request)

    # CSRF-Double-Submit-Cookie: falls noch nicht gesetzt, initialisieren.
    if not request.cookies.get("csrf_token"):
        response.set_cookie(
            key="csrf_token",
            value=secrets.token_urlsafe(32),
            httponly=False,
            secure=settings.ENVIRONMENT != "development",
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
            path="/",
        )

    # Content-Security-Policy mit Nonce für zukünftige HTML-Ausgaben.
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        f"img-src 'self' data:; "
        f"font-src 'self'; "
        f"connect-src 'self'; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


# Audit-Middleware nach CORS/Security-Header einbinden, damit Responses sichtbar sind.
from app.middleware.audit import AuditMiddleware  # noqa: E402

app.add_middleware(AuditMiddleware)


# Routes (imported after app creation to avoid circular imports)
from app.routes import auth, dsgvo, einwilligungen, health  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(einwilligungen.router, prefix="/api/v1/einwilligungen", tags=["einwilligungen"])
app.include_router(dsgvo.router, prefix="/api/v1/dsgvo", tags=["dsgvo"])
app.include_router(health.router, tags=["health"])
