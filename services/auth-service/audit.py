import json
import logging
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from aiokafka import AIOKafkaProducer

from models import AuditLog
from config import settings

logger = logging.getLogger(__name__)

producer: Optional[AIOKafkaProducer] = None

async def init_kafka():
    global producer
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()
        logger.info("Kafka producer started.")
    except Exception as e:
        logger.error(f"Failed to start Kafka producer: {e}")

async def close_kafka():
    global producer
    if producer:
        await producer.stop()

async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource: str,
    result: str,
    actor_id: Optional[int] = None,
    details: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    # Save to database
    audit_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address,
        result=result
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(audit_entry)

    # Publish to Kafka
    if producer:
        event = {
            "id": audit_entry.id,
            "actor_id": actor_id,
            "action": action,
            "resource": resource,
            "details": details,
            "ip_address": ip_address,
            "result": result,
            "timestamp": audit_entry.timestamp.isoformat()
        }
        try:
            await producer.send_and_wait("audit.events", event)
        except Exception as e:
            logger.error(f"Failed to publish audit event to Kafka: {e}")
