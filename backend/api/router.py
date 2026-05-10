from fastapi import APIRouter
from .endpoints import health, logs_ws, agents_ws, incidents

api_router = APIRouter()

# Health endpoint
api_router.include_router(health.router, prefix="/health", tags=["health"])

# WebSocket endpoints - use /ws prefix to match frontend
api_router.include_router(logs_ws.router, prefix="/ws", tags=["websockets"])
api_router.include_router(agents_ws.router, prefix="/ws", tags=["websockets"])

# HTTP API endpoints - use /api prefix to match frontend
api_router.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
