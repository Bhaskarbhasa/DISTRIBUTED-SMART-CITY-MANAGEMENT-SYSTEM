import paho.mqtt.client as mqtt
import json
import structlog
import asyncio
from config import settings
from processors.traffic_processor import process_traffic
from processors.environment_processor import process_environment
from processors.emergency_processor import process_emergency
from models import CameraEvent
from kafka_producer import kafka_manager

logger = structlog.get_logger()

REGISTERED_DEVICES = {
    "TRAFFIC-ZONE-A-001", "TRAFFIC-ZONE-A-002",
    "ENV-ZONE-A-001", "CAM-ZONE-A-001",
    "EMERGENCY-SYS-01"
}

class MQTTGateway:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="edge-gateway-01")
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
            
        self.loop = None
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def start(self):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
        logger.info("connecting_to_mqtt", broker=settings.MQTT_BROKER, port=settings.MQTT_PORT)
        try:
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error("mqtt_connection_failed", error=str(e))
            
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        logger.info("mqtt_connected", reason_code=reason_code)
        topics = [
            ("city/traffic/#", 1),
            ("city/environment/#", 1),
            ("city/emergency/#", 1),
            ("city/camera/#", 1)
        ]
        client.subscribe(topics)
        
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            sensor_id = payload.get('sensor_id') or payload.get('camera_id') or payload.get('source_id')
            
            if not sensor_id or (sensor_id not in REGISTERED_DEVICES and not sensor_id.startswith("TRAFFIC-") and not sensor_id.startswith("ENV-") and not sensor_id.startswith("CAM-") and not sensor_id.startswith("EMERGENCY-")):
                logger.warning("unknown_device_rejected", sensor_id=sensor_id)
                
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self.process_message(msg.topic, payload), self.loop)
        except Exception as e:
            logger.error("mqtt_message_processing_failed", error=str(e), topic=msg.topic)
            
    async def process_message(self, topic: str, payload: dict):
        try:
            if topic.startswith("city/traffic/"):
                event = process_traffic(payload)
                await kafka_manager.send_event("traffic.telemetry", event.model_dump(), event.zone_id)
            elif topic.startswith("city/environment/"):
                event = process_environment(payload)
                await kafka_manager.send_event("environment.telemetry", event.model_dump(), event.zone_id)
            elif topic.startswith("city/emergency/"):
                if "sensor_id" not in payload:
                     payload["sensor_id"] = "EMERGENCY-SYS"
                event = process_emergency(payload)
                await kafka_manager.send_event("emergency.alert", event.model_dump(), event.zone_id)
            elif topic.startswith("city/camera/"):
                if "sensor_id" not in payload:
                    payload["sensor_id"] = payload.get("camera_id", "CAM-UNKNOWN")
                event = CameraEvent(**payload)
                await kafka_manager.send_event("camera.telemetry", event.model_dump(), event.zone_id)
            else:
                logger.warning("unknown_topic", topic=topic)
        except Exception as e:
            logger.error("event_processing_error", error=str(e), topic=topic)

mqtt_gateway = MQTTGateway()
