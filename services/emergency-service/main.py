from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import json

from database import init_db, get_db
from kafka_consumer import kafka_manager
from models import EmergencyAlert, AlertAuditLog
from websocket_manager import manager

app = FastAPI(title='Emergency Service')

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

@app.get('/emergency/alerts')
async def get_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.status == 'ACTIVE'))
    return result.scalars().all()

@app.get('/emergency/alerts/{alert_id}')
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    return alert

@app.post('/emergency/alerts/{alert_id}/acknowledge')
async def ack_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')

    alert.status = 'ACKNOWLEDGED'
    alert.acknowledged_at = datetime.now(timezone.utc)

    audit = AlertAuditLog(alert_id=alert_id, action='ACKNOWLEDGED', actor='user')
    db.add(audit)
    await db.commit()
    await manager.broadcast(json.dumps({'type': 'alert_update', 'alert_id': alert_id, 'status': 'ACKNOWLEDGED'}))
    return {'status': 'acknowledged'}

@app.put('/emergency/alerts/{alert_id}/resolve')
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyAlert).where(EmergencyAlert.alert_id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')

    alert.status = 'RESOLVED'
    alert.resolved_at = datetime.now(timezone.utc)

    audit = AlertAuditLog(alert_id=alert_id, action='RESOLVED', actor='user')
    db.add(audit)
    await db.commit()
    await manager.broadcast(json.dumps({'type': 'alert_update', 'alert_id': alert_id, 'status': 'RESOLVED'}))
    return {'status': 'resolved'}

@app.get('/emergency/history')
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyAlert).order_by(EmergencyAlert.reported_at.desc()).limit(100))
    return result.scalars().all()

@app.websocket('/ws/emergency')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
