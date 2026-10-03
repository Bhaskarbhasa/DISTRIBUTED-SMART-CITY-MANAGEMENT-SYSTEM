import asyncio
import json
import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from config import settings
from fog_client import get_traffic_decision
from redis_cache import set_traffic_state, set_signal_state
from websocket_manager import manager
from database import AsyncSessionLocal
from models import TrafficTelemetry, TrafficDecision
from metrics import TRAFFIC_CONGESTION, DECISION_COUNT

logger = structlog.get_logger()

class TrafficKafkaManager:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'traffic.telemetry',
            bootstrap_servers=settings.KAFKA_BROKERS,
            group_id='traffic-service',
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
                logger.info('received_telemetry', data=data)
                await self.process_telemetry(data)
        except Exception as e:
            logger.error('kafka_consumer_error', error=str(e))

    async def process_telemetry(self, data: dict):
        zone_id = data.get('zone_id')
        congestion_level = data.get('congestion_level')
        if not zone_id or congestion_level is None:
            return

        try:
            congestion_value = float(congestion_level)
        except ValueError:
            congestion_value = 0.0

        TRAFFIC_CONGESTION.labels(zone_id=zone_id).set(congestion_value)

        # Store state in Redis
        await set_traffic_state(zone_id, data)

        if congestion_value > 50:
            decision = await get_traffic_decision(zone_id, int(congestion_value))
            decision['zone_id'] = zone_id

            # Metrics
            DECISION_COUNT.labels(zone_id=zone_id, signal_state=decision.get('signal_state')).inc()

            # Redis
            await set_signal_state(zone_id, decision)

            # Broadcast
            await manager.broadcast(json.dumps({'type': 'decision', 'data': decision}))

            # Kafka Producer
            await self.producer.send_and_wait('traffic.decision', decision)

            # DB
            async with AsyncSessionLocal() as session:
                # Save telemetry
                telemetry = TrafficTelemetry(**data)
                session.add(telemetry)

                # Save decision
                durations = decision.get('durations', {})
                db_decision = TrafficDecision(
                    decision_id=decision.get('decision_id'),
                    zone_id=zone_id,
                    signal_state=decision.get('signal_state'),
                    green_duration=durations.get('green', 0),
                    yellow_duration=durations.get('yellow', 0),
                    red_duration=durations.get('red', 0),
                    leader_id=decision.get('leader_id')
                )
                session.add(db_decision)
                await session.commit()

kafka_manager = TrafficKafkaManager()
