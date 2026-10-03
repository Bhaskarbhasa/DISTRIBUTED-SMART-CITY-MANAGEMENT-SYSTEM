import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from prometheus_client import make_asgi_app, Counter, Histogram
from config import settings
from structlog import get_logger
import kafka_consumer
import redis_cache
from typing import List

logger = get_logger()
app = FastAPI(title="Environment Service")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kafka_consumer.start_kafka_consumer())
    asyncio.create_task(broadcast_updates())

async def broadcast_updates():
    while True:
        try:
            zones = await redis_cache.get_latest_zones()
            import json
            if zones:
                await manager.broadcast(json.dumps({"type": "ENV_UPDATE", "data": zones}))
        except Exception as e:
            logger.error("Error in broadcast", error=str(e))
        await asyncio.sleep(5)

@app.get("/environment/zones")
async def get_zones():
    return await redis_cache.get_latest_zones()

@app.get("/environment/zones/{zone_id}")
async def get_zone(zone_id: str):
    return await redis_cache.get_zone_details(zone_id)

@app.get("/environment/history")
async def get_history(zone_id: str = None, limit: int = 10):
    if not zone_id:
        return {"error": "zone_id required"}
    return await redis_cache.get_zone_history(zone_id, limit)

@app.get("/environment/alerts")
async def get_alerts():
    return await redis_cache.get_active_alerts()

@app.websocket("/ws/environment")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}
