from fastapi import FastAPI, HTTPException, Depends
from prometheus_client import make_asgi_app
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aiokafka import AIOKafkaProducer
import json
import datetime
import asyncio
from typing import List

from config import settings
from models import Base, Device, DeviceRegister, DeviceStatusUpdate, DeviceResponse

logger = structlog.get_logger()

# DB Setup
engine = create_async_engine(settings.database_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Kafka Setup
producer: AIOKafkaProducer = None

async def get_db():
    async with async_session() as session:
        yield session

app = FastAPI(title="Ingestion Service")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    global producer
    
    # Init DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Init Kafka Producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    try:
        await producer.start()
        logger.info("kafka_producer_started")
    except Exception as e:
        logger.error("kafka_producer_start_failed", error=str(e))
        # Don't crash app if Kafka isn't ready immediately in dev
        
@app.on_event("shutdown")
async def shutdown_event():
    if producer:
        await producer.stop()
    await engine.dispose()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.post("/devices/register", response_model=DeviceResponse)
async def register_device(device: DeviceRegister, db: AsyncSession = Depends(get_db)):
    # Check if exists
    db_device = await db.get(Device, device.device_id)
    if db_device:
        raise HTTPException(status_code=400, detail="Device already registered")
        
    new_device = Device(
        device_id=device.device_id,
        device_type=device.device_type,
        location_zone=device.location_zone,
        credentials=device.credentials,
        metadata_json=device.metadata_json,
        status="active"
    )
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)
    logger.info("device_registered", device_id=device.device_id)
    return new_device

@app.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(Device))
    return result.scalars().all()

@app.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.put("/devices/{device_id}/status")
async def update_device_status(device_id: str, status_update: DeviceStatusUpdate, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device.status = status_update.status
    device.last_seen = datetime.datetime.utcnow()
    
    if status_update.metadata_update:
        device.metadata_json.update(status_update.metadata_update)
        
    await db.commit()
    
    # Publish to Kafka
    event = {
        "event_type": "device_status_changed",
        "device_id": device.device_id,
        "status": device.status,
        "timestamp": device.last_seen.isoformat(),
        "metadata": device.metadata_json
    }
    
    try:
        if producer:
            await producer.send_and_wait(settings.kafka_topic_devices, event)
    except Exception as e:
        logger.error("kafka_publish_failed", error=str(e), device_id=device_id)
        
    return {"message": "Status updated successfully"}

@app.delete("/devices/{device_id}")
async def deregister_device(device_id: str, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    await db.delete(device)
    await db.commit()
    logger.info("device_deregistered", device_id=device_id)
    return {"message": "Device deregistered successfully"}
