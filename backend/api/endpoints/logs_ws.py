from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import asyncio
from utils.log_generator import log_stream_generator
from agents.agent_manager import run_monitor_agent

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    logger.info("✅ Client connected to log stream")
    
    try:
        async for log_entry in log_stream_generator():
            try:
                await websocket.send_json(log_entry.model_dump())
                asyncio.create_task(run_monitor_agent(log_entry))
            except:
                break
                
    except WebSocketDisconnect:
        logger.info("Client disconnected from log stream")
    except Exception as e:
        logger.info(f"Log stream ended: {e}")
    finally:
        logger.info("Log stream connection closed")
