# Import all routes to make them available when importing from tts_gateway.api
from tts_gateway.api.v1.routes_health import router as health_router
from tts_gateway.api.v1.routes_tts import router as tts_router

__all__ = ["health_router", "tts_router"]
