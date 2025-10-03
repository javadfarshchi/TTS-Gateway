"""API router configuration."""

from fastapi import APIRouter

from .v1.routes_health import router as health_router
from .v1.routes_tts import router as tts_router

api = APIRouter()
api.include_router(health_router, prefix="/api/v1")
api.include_router(tts_router, prefix="/api/v1")
