from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@router.websocket("/agents")
async def websocket_agents(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("✅ Client connected to agent state stream")
    
    try:
        # Just keep the connection open
        while True:
            await websocket.receive_text()
                
    except WebSocketDisconnect:
        logger.info("Client disconnected from agent state stream")
    except Exception as e:
        logger.info(f"Agent stream ended: {e}")
    finally:
        manager.disconnect(websocket)
        logger.info("Agent stream connection closed")

async def notify_agent_state(agent_name: str, status: str, message: str, details: dict = None):
    payload = {
        "agent": agent_name,
        "status": status,
        "message": message,
        "details": details or {}
    }
    await manager.broadcast(payload)
