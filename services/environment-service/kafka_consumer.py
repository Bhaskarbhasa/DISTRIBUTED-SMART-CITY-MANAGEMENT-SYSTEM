import json
import asyncio
import uuid
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from structlog import get_logger
from models import EnvironmentTelemetry, EnvironmentAlert
from config import settings
import redis_cache

logger = get_logger()

producer = None

async def start_kafka_consumer():
    global producer
    consumer = AIOKafkaConsumer(
        settings.ENVIRONMENT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKERS,
        group_id=settings.CONSUMER_GROUP,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    
    await consumer.start()
    await producer.start()
    logger.info("Kafka consumer/producer started")
    
    try:
        async for msg in consumer:
            data = msg.value
            telemetry = EnvironmentTelemetry(**data)
            await process_telemetry(telemetry)
    except Exception as e:
        logger.error("Error consuming messages", error=str(e))
    finally:
        await consumer.stop()
        await producer.stop()

async def process_telemetry(telemetry: EnvironmentTelemetry):
    await redis_cache.cache_telemetry(telemetry)
    
    alerts = []
    
    # AQI > 100: MODERATE alert
    # AQI > 150: UNHEALTHY alert  
    # AQI > 200: VERY_UNHEALTHY alert
    # AQI > 300: HAZARDOUS alert (emergency)
    if telemetry.aqi > 300:
        alerts.append(("HAZARDOUS", telemetry.aqi, 300))
    elif telemetry.aqi > 200:
        alerts.append(("VERY_UNHEALTHY", telemetry.aqi, 200))
    elif telemetry.aqi > 150:
        alerts.append(("UNHEALTHY", telemetry.aqi, 150))
    elif telemetry.aqi > 100:
        alerts.append(("MODERATE", telemetry.aqi, 100))
        
    # Temperature > 45°C or < -5°C: EXTREME alert
    if telemetry.temperature > 45 or telemetry.temperature < -5:
        alerts.append(("EXTREME_TEMP", telemetry.temperature, 45 if telemetry.temperature > 45 else -5))
        
    # PM2.5 > 35: UNHEALTHY
    if telemetry.pm25 > 35:
        alerts.append(("UNHEALTHY_PM25", telemetry.pm25, 35))
        
    for severity, value, threshold in alerts:
        alert = EnvironmentAlert(
            alert_id=str(uuid.uuid4()),
            zone_id=telemetry.zone_id,
            alert_type="ENVIRONMENTAL",
            severity=severity,
            value=value,
            threshold=threshold
        )
        await redis_cache.cache_alert(alert)
        if producer:
            await producer.send_and_wait(settings.ALERT_TOPIC, alert.model_dump(mode="json"))
            logger.info("Alert generated", alert=alert.model_dump(mode="json"))
