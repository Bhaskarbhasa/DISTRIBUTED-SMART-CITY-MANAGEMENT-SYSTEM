import asyncio
from fastapi import FastAPI, HTTPException
import structlog
from prometheus_client import make_asgi_app

from mqtt_handler import mqtt_gateway
from kafka_producer import kafka_manager
from buffer import EventBuffer

logger = structlog.get_logger()
app = FastAPI(title="Edge Gateway")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

buffer = EventBuffer()

@app.on_event("startup")
async def startup_event():
    await kafka_manager.start()
    mqtt_gateway.start()
    logger.info("edge_gateway_started")

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_gateway.stop()
    await kafka_manager.stop()
    logger.info("edge_gateway_stopped")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {
        "status": "ok", 
        "mqtt_connected": mqtt_gateway.client.is_connected(),
        "kafka_connected": kafka_manager.connected
    }

@app.get("/buffer/status")
def buffer_status():
    count = buffer.count_buffered()
    return {"buffered_events": count}

@app.post("/buffer/flush")
async def flush_buffer():
    if not kafka_manager.connected:
        raise HTTPException(status_code=503, detail="Kafka not connected")
    
    events = buffer.get_pending_events(limit=100)
    return {"status": "flush_initiated", "events_to_flush": len(events)}

@app.get("/devices")
def list_devices():
    from mqtt_handler import REGISTERED_DEVICES
    return {"devices": list(REGISTERED_DEVICES)}
