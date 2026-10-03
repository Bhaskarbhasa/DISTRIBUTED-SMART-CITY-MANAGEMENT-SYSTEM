import json
import asyncio
import structlog
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from config import settings

logger = structlog.get_logger()

class KafkaClient:
    def __init__(self):
        self.producer = None
        self.consumer = None

    async def start(self):
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka producer started")
            
            # Start consumer for raft.events
            self.consumer = AIOKafkaConsumer(
                'raft.events',
                bootstrap_servers=settings.KAFKA_BROKERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id=f"fog-node-{settings.FOG_NODE_ID}"
            )
            await self.consumer.start()
            asyncio.create_task(self.consume_events())
            logger.info("Kafka consumer started")
        except Exception as e:
            logger.error("Failed to start Kafka client", error=str(e))

    async def stop(self):
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()

    async def publish_leader_change(self, term: int, leader_id: str):
        if self.producer:
            await self.producer.send_and_wait(
                'raft.events',
                {"event": "leader_change", "term": term, "leader_id": leader_id}
            )

    async def publish_traffic_decision(self, decision: dict):
        if self.producer:
            await self.producer.send_and_wait(
                'traffic.decision',
                decision
            )

    async def consume_events(self):
        try:
            async for msg in self.consumer:
                logger.debug("Received Kafka event", topic=msg.topic, value=msg.value)
        except Exception as e:
            logger.error("Error consuming Kafka events", error=str(e))

kafka_client = KafkaClient()
