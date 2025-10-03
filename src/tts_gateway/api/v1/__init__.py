"""API v1 routes."""

from fastapi import APIRouter

# Import routes directly to avoid circular imports
from .routes_health import router as health_router
from .routes_tts import router as tts_router

# Create the main API v1 router
router = APIRouter(prefix="")
router.include_router(health_router)
router.include_router(tts_router)
