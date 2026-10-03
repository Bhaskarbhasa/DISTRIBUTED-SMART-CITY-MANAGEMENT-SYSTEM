import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from prometheus_client import make_asgi_app
import kafka_consumer
from websocket_manager import manager

app = FastAPI(title="Notification Service")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kafka_consumer.start_kafka_consumers())

@app.get("/notifications/recent")
async def get_recent():
    return kafka_consumer.notification_buffer[:100]

@app.websocket("/ws/notifications")
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
