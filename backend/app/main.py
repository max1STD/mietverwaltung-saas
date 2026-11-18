"""FastAPI application factory for MietVerwaltung SaaS."""
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.config import settings
from app.lifespan import shutdown, startup


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
async def security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
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
from app.routes import (
    abrechnungen,
    admin,
    auth,
    bankverbindungen,
    bewerbungen,
    billing,
    dashboard,
    dokumente,
    dsgvo,
    einheiten,
    einwilligungen,
    geo,
    health,
    ki,
    kosten,
    kostenkategorien,
    mieter,
    mietvertraege,
    mietzahlungen,
    objekte,
    onboarding,
    stripe_webhooks,
    tickets,
    zaehler,
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(einwilligungen.router, prefix="/api/v1/einwilligungen", tags=["einwilligungen"])
app.include_router(dsgvo.router, prefix="/api/v1/dsgvo", tags=["dsgvo"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(objekte.router, prefix="/api/v1/objekte", tags=["objekte"])
app.include_router(bankverbindungen.router, prefix="/api/v1/bankverbindungen", tags=["bankverbindungen"])
app.include_router(einheiten.router, prefix="/api/v1/einheiten", tags=["einheiten"])
app.include_router(mieter.router, prefix="/api/v1/mieter", tags=["mieter"])
app.include_router(mietvertraege.router, prefix="/api/v1/mietvertraege", tags=["mietvertraege"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(kosten.router, prefix="/api/v1/kosten", tags=["kosten"])
app.include_router(kostenkategorien.router, prefix="/api/v1/kostenkategorien", tags=["kostenkategorien"])
app.include_router(abrechnungen.router, prefix="/api/v1/abrechnungen", tags=["abrechnungen"])
app.include_router(mietzahlungen.router, prefix="/api/v1/mietzahlungen", tags=["mietzahlungen"])
app.include_router(bewerbungen.router, prefix="/api/v1/bewerbungen", tags=["bewerbungen"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(stripe_webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(health.router, tags=["health"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(ki.router, prefix="/api/v1/ki", tags=["ki"])
app.include_router(dokumente.router, prefix="/api/v1/dokumente", tags=["dokumente"])
app.include_router(geo.router, prefix="/api/v1/geo", tags=["geo"])
app.include_router(zaehler.router, prefix="/api/v1/zaehler", tags=["zaehler"])
