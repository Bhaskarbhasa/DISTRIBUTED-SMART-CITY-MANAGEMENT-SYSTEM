import asyncio
import json
import structlog
from aiokafka import AIOKafkaProducer
from config import settings
from buffer import EventBuffer
import random

logger = structlog.get_logger()
buffer = EventBuffer()

class KafkaManager:
    def __init__(self):
        self.producer = None
        self.connected = False
        self._flush_task = None
        
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        try:
            await self.producer.start()
            self.connected = True
            logger.info("kafka_connected")
            self._flush_task = asyncio.create_task(self.flush_buffer_loop())
        except Exception as e:
            logger.error("kafka_connection_failed", error=str(e))
            self.connected = False
            
    async def stop(self):
        if self._flush_task:
            self._flush_task.cancel()
        if self.producer:
            await self.producer.stop()
            self.connected = False
            
    async def send_event(self, topic: str, payload: dict, partition_key: str = None):
        if not self.connected:
            buffer.add_event(topic, payload)
            return
            
        try:
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    await self.producer.send_and_wait(
                        topic, 
                        value=payload, 
                        key=partition_key.encode('utf-8') if partition_key else None
                    )
                    return
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error("kafka_send_failed_buffering", error=str(e))
            buffer.add_event(topic, payload)
            self.connected = False
            
    async def flush_buffer_loop(self):
        while True:
            if self.connected:
                events = buffer.get_pending_events(limit=50)
                for event in events:
                    try:
                        payload = json.loads(event['payload'])
                        zone_id = payload.get('zone_id')
                        await self.producer.send_and_wait(
                            event['topic'],
                            value=payload,
                            key=zone_id.encode('utf-8') if zone_id else None
                        )
                        buffer.remove_event(event['id'])
                    except Exception as e:
                        buffer.increment_retry_or_dead_letter(event['id'], event['topic'], event['payload'], str(e))
                        self.connected = False
                        break
            await asyncio.sleep(10)
            
kafka_manager = KafkaManager()
