import json
import asyncio
from aiokafka import AIOKafkaConsumer
from structlog import get_logger
from config import settings
from websocket_manager import manager
from typing import List, Dict

logger = get_logger()

# In-memory buffer
notification_buffer: List[Dict] = []
BUFFER_SIZE = 1000

async def start_kafka_consumers():
    topics = ["traffic.congestion", "emergency.alert", "raft.events", "system.events", "environment.alert"]
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.KAFKA_BROKERS,
        group_id=settings.CONSUMER_GROUP,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    
    await consumer.start()
    logger.info("Kafka consumer started", topics=topics)
    
    try:
        async for msg in consumer:
            await process_message(msg.topic, msg.value)
    except Exception as e:
        logger.error("Error consuming messages", error=str(e))
    finally:
        await consumer.stop()

async def process_message(topic: str, data: dict):
    category = "SYSTEM"
    if topic == "traffic.congestion":
        category = "TRAFFIC"
    elif topic == "emergency.alert":
        category = "EMERGENCY"
    elif topic == "raft.events":
        category = "RAFT"
    elif topic == "environment.alert":
        category = "ENVIRONMENT"
        
    notification = {
        "category": category,
        "topic": topic,
        "data": data,
        "timestamp": data.get("timestamp", "now")
    }
    
    notification_buffer.insert(0, notification)
    if len(notification_buffer) > BUFFER_SIZE:
        notification_buffer.pop()
        
    await manager.broadcast(notification)
    if category == "EMERGENCY":
        logger.warn("EMERGENCY NOTIFICATION", data=data)
    else:
        logger.info("Notification processed", category=category, topic=topic)
