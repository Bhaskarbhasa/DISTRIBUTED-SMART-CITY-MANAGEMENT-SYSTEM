import asyncio
import json
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import init_db, get_db
from kafka_consumer import kafka_manager
from websocket_manager import manager
from redis_cache import get_all_zones_state, get_traffic_state, get_all_signals_state, get_signal_state, set_signal_state
from traffic_controller import get_emergency_override
from models import TrafficTelemetry

app = FastAPI(title='Traffic Service')

@app.on_event('startup')
async def startup_event():
    await init_db()
    await kafka_manager.start()

@app.on_event('shutdown')
async def shutdown_event():
    await kafka_manager.stop()

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.get('/ready')
async def ready():
    return {'status': 'ready'}

@app.get('/metrics')
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get('/traffic/zones')
async def get_zones():
    return await get_all_zones_state()

@app.get('/traffic/zones/{zone_id}')
async def get_zone(zone_id: str):
    state = await get_traffic_state(zone_id)
    if not state:
        raise HTTPException(status_code=404, detail='Zone not found')
    return state

@app.get('/traffic/signals')
async def get_signals():
    return await get_all_signals_state()

@app.put('/traffic/signals/{zone_id}')
async def override_signal(zone_id: str):
    decision = get_emergency_override()
    decision['zone_id'] = zone_id
    await set_signal_state(zone_id, decision)
    await manager.broadcast(json.dumps({'type': 'override', 'data': decision}))
    await kafka_manager.producer.send_and_wait('traffic.decision', decision)
    return decision

@app.get('/traffic/history')
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrafficTelemetry).order_by(TrafficTelemetry.timestamp.desc()).limit(100))
    return result.scalars().all()

@app.websocket('/ws/traffic')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
