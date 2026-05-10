from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

from core.config import settings
from utils.logger import setup_logger
from api.router import api_router
from utils.metrics_monitor import metrics_monitor

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for Self-Healing Cloud Guardian",
    version=settings.VERSION
)

# Add CORS middleware - explicitly allow frontend origins for WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,  # Required for WebSocket connections
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status": "SRE Guardian Backend is running"}

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Server starting up...")
    logger.info("Available routes:")
    for route in app.routes:
        logger.info(f"  {route.path} - {route.name}")
    logger.info("=" * 60)
    
    # Start real-time metrics monitoring if enabled
    if settings.ENABLE_REAL_METRICS_MONITORING:
        logger.info("🔍 Real-time metrics monitoring is ENABLED")
        asyncio.create_task(metrics_monitor.start_monitoring())
    else:
        logger.info("⏸️  Real-time metrics monitoring is DISABLED")
        logger.info("   Set ENABLE_REAL_METRICS_MONITORING=true in .env to enable")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    metrics_monitor.stop_monitoring()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
