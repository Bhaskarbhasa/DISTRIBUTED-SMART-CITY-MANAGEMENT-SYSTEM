import asyncio
import json
import structlog
import httpx
import uuid
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from config import settings
from deduplication import is_duplicate
from database import AsyncSessionLocal
from models import EmergencyAlert, AlertAuditLog
from websocket_manager import manager

logger = structlog.get_logger()

class EmergencyKafkaManager:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'emergency.alert',
            bootstrap_servers=settings.KAFKA_BROKERS,
            group_id='emergency-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    async def start(self):
        await self.consumer.start()
        await self.producer.start()
        asyncio.create_task(self.consume())

    async def stop(self):
        await self.consumer.stop()
        await self.producer.stop()

    async def consume(self):
        try:
            async for msg in self.consumer:
                data = msg.value
                logger.info('received_emergency_alert', data=data)
                await self.process_alert(data)
        except Exception as e:
            logger.error('kafka_consumer_error', error=str(e))

    async def process_alert(self, data: dict):
        event_id = data.get('event_id')
        if not event_id:
            return

        if await is_duplicate(event_id):
            logger.info('duplicate_alert_skipped', event_id=event_id)
            return

        alert_id = str(uuid.uuid4())
        data['alert_id'] = alert_id

        async with AsyncSessionLocal() as session:
            alert = EmergencyAlert(
                alert_id=alert_id,
                event_id=event_id,
                alert_type=data.get('alert_type'),
                severity=data.get('severity'),
                location_lat=data.get('location_lat'),
                location_lon=data.get('location_lon'),
                zone_id=data.get('zone_id')
            )
            session.add(alert)

            audit = AlertAuditLog(
                alert_id=alert_id,
                action='CREATED',
                actor='system'
            )
            session.add(audit)
            await session.commit()

        # Broadcast
        await manager.broadcast(json.dumps({'type': 'new_alert', 'data': data}))

        if data.get('severity') == 'CRITICAL':
            zone_id = data.get('zone_id')
            if zone_id:
                try:
                    async with httpx.AsyncClient() as client:
                        await client.put(f"{settings.TRAFFIC_SERVICE_URL}/traffic/signals/{zone_id}")
                except Exception as e:
                    logger.error('failed_to_override_traffic', error=str(e))

            await self.producer.send_and_wait('system.events', {'event_type': 'CRITICAL_EMERGENCY', 'data': data})

kafka_manager = EmergencyKafkaManager()
