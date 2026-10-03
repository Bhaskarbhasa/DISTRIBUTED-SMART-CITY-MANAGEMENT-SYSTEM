from fastapi import WebSocket
from typing import List
import json
from structlog import get_logger

logger = get_logger()

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        msg_str = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(msg_str)
            except Exception:
                dead_connections.append(connection)
                
        for connection in dead_connections:
            self.disconnect(connection)

manager = WebSocketManager()
