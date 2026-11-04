"""Auth routes — registration, login, 2FA, refresh."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """Register a new Vermieter account."""
    # TODO: Implement
    return {"message": "Not yet implemented"}


@router.post("/login")
async def login():
    """Login with email + password."""
    # TODO: Implement
    return {"message": "Not yet implemented"}


@router.post("/2fa/verify")
async def verify_2fa():
    """Verify TOTP or E-Mail code."""
    # TODO: Implement
    return {"message": "Not yet implemented"}


@router.post("/refresh")
async def refresh_token():
    """Refresh JWT access token."""
    # TODO: Implement
    return {"message": "Not yet implemented"}
