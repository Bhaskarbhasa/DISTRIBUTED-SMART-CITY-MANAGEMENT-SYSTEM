import os

base_dir = r"d:\Distributed_system\Smart_DS_Project\distributed-smart-city\edge"

files = {
    "edge-gateway/requirements.txt": """fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.2
paho-mqtt==2.1.0
aiokafka==0.11.0
structlog==24.4.0
prometheus-client==0.21.0
""",
    "edge-gateway/Dockerfile": """FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "edge-gateway/config.py": """import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "admin")
    
    KAFKA_BROKERS: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    
    DB_PATH: str = os.getenv("DB_PATH", "buffer.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
""",
    "edge-gateway/models.py": """from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class BaseEvent(BaseModel):
    sensor_id: str
    zone_id: str
    timestamp: str
    processing_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TrafficEvent(BaseEvent):
    vehicle_count: int
    average_speed: float
    lane_count: int
    lane_occupancy: List[float]
    
    congestion_level: Optional[str] = None
    density: Optional[float] = None
    anomaly_score: Optional[float] = None

class EnvironmentEvent(BaseEvent):
    temperature: float
    humidity: float
    aqi: float
    pm25: float
    pm10: float
    co2: float
    no2: float
    wind_speed: float
    wind_direction: float
    
    air_quality_category: Optional[str] = None
    temperature_alert: Optional[bool] = None

class EmergencyEvent(BaseEvent):
    emergency_type: str
    severity: str
    location: dict
    
    priority: Optional[int] = None

class CameraEvent(BaseEvent):
    camera_id: str
    vehicle_count: int
    pedestrian_count: int
    incident_detected: bool
    incident_type: Optional[str] = None
    confidence: float
""",
    "edge-gateway/buffer.py": """import sqlite3
import json
import structlog
from typing import List, Dict, Any
from config import settings

logger = structlog.get_logger()

class EventBuffer:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    retries INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dead_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def add_event(self, topic: str, payload: dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO events (topic, payload) VALUES (?, ?)",
                    (topic, json.dumps(payload))
                )
            logger.info("event_buffered", topic=topic)
        except Exception as e:
            logger.error("buffer_add_failed", error=str(e))
            
    def get_pending_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM events ORDER BY created_at ASC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
            
    def remove_event(self, event_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
    def increment_retry_or_dead_letter(self, event_id: int, topic: str, payload: str, error: str, max_retries: int = 5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT retries FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                retries = row[0]
                if retries >= max_retries:
                    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
                    conn.execute(
                        "INSERT INTO dead_letters (topic, payload, error) VALUES (?, ?, ?)",
                        (topic, payload, error)
                    )
                    logger.warning("event_dead_lettered", event_id=event_id, topic=topic)
                else:
                    conn.execute("UPDATE events SET retries = retries + 1 WHERE id = ?", (event_id,))
                    
    def count_buffered(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]
""",
    "edge-gateway/kafka_producer.py": """import asyncio
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
""",
    "edge-gateway/processors/__init__.py": "",
    "edge-gateway/processors/traffic_processor.py": """from models import TrafficEvent

def process_traffic(data: dict) -> TrafficEvent:
    event = TrafficEvent(**data)
    
    if event.vehicle_count < 30:
        event.congestion_level = "LOW"
    elif 30 <= event.vehicle_count <= 70:
        event.congestion_level = "MEDIUM"
    elif 71 <= event.vehicle_count <= 100:
        event.congestion_level = "HIGH"
    else:
        event.congestion_level = "CRITICAL"
        
    event.density = event.vehicle_count / (event.lane_count * 1000.0) if event.lane_count else 0.0
    
    event.anomaly_score = 0.0
    if event.vehicle_count > 80 and event.average_speed > 60:
        event.anomaly_score = 0.8
    elif event.vehicle_count < 10 and event.average_speed < 10:
        event.anomaly_score = 0.6
        
    return event
""",
    "edge-gateway/processors/environment_processor.py": """from models import EnvironmentEvent

def process_environment(data: dict) -> EnvironmentEvent:
    event = EnvironmentEvent(**data)
    
    if event.aqi <= 100:
        event.air_quality_category = "GOOD" if event.aqi <= 50 else "MODERATE"
    elif event.aqi <= 150:
        event.air_quality_category = "UNHEALTHY_SENSITIVE"
    elif event.aqi <= 200:
        event.air_quality_category = "UNHEALTHY"
    elif event.aqi <= 300:
        event.air_quality_category = "VERY_UNHEALTHY"
    else:
        event.air_quality_category = "HAZARDOUS"
        
    event.temperature_alert = event.temperature > 40 or event.temperature < -5
    
    return event
""",
    "edge-gateway/processors/emergency_processor.py": """from models import EmergencyEvent

def process_emergency(data: dict) -> EmergencyEvent:
    event = EmergencyEvent(**data)
    
    priority_map = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    
    base_priority = priority_map.get(event.severity.upper(), 1)
    if event.emergency_type.upper() in ["FIRE", "MEDICAL"]:
        base_priority += 1
        
    event.priority = min(base_priority, 5)
    return event
""",
    "edge-gateway/mqtt_handler.py": """import paho.mqtt.client as mqtt
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
            
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def start(self):
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
                
            asyncio.run_coroutine_threadsafe(self.process_message(msg.topic, payload), asyncio.get_event_loop())
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
""",
    "edge-gateway/main.py": """import asyncio
from fastapi import FastAPI, HTTPException
import structlog
from prometheus_client import make_asgi_app

from mqtt_handler import mqtt_gateway
from kafka_producer import kafka_manager
from buffer import EventBuffer

logger = structlog.get_logger()
app = FastAPI(title="Edge Gateway")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

buffer = EventBuffer()

@app.on_event("startup")
async def startup_event():
    await kafka_manager.start()
    mqtt_gateway.start()
    logger.info("edge_gateway_started")

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_gateway.stop()
    await kafka_manager.stop()
    logger.info("edge_gateway_stopped")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {
        "status": "ok", 
        "mqtt_connected": mqtt_gateway.client.is_connected(),
        "kafka_connected": kafka_manager.connected
    }

@app.get("/buffer/status")
def buffer_status():
    count = buffer.count_buffered()
    return {"buffered_events": count}

@app.post("/buffer/flush")
async def flush_buffer():
    if not kafka_manager.connected:
        raise HTTPException(status_code=503, detail="Kafka not connected")
    
    events = buffer.get_pending_events(limit=100)
    return {"status": "flush_initiated", "events_to_flush": len(events)}

@app.get("/devices")
def list_devices():
    from mqtt_handler import REGISTERED_DEVICES
    return {"devices": list(REGISTERED_DEVICES)}
""",
    "traffic-simulator/requirements.txt": """fastapi==0.115.0
uvicorn==0.30.6
paho-mqtt==2.1.0
structlog==24.4.0
pydantic==2.9.2
pydantic-settings==2.5.2
""",
    "traffic-simulator/Dockerfile": """FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
""",
    "traffic-simulator/config.py": """import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "admin")
    
    class Config:
        env_file = ".env"

settings = Settings()
""",
    "traffic-simulator/main.py": """import asyncio
import argparse
import random
import json
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import paho.mqtt.client as mqtt
import structlog
from config import settings

logger = structlog.get_logger()
app = FastAPI(title="Traffic Simulator")

class SimulatorState:
    def __init__(self):
        self.mode = "normal"
        self.rate = 2.0
        self.zone = "all"
        self.running = True
        self.forced_zone = None
        self.forced_mode = None

state = SimulatorState()
mqtt_client = None

def init_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"traffic-sim-{random.randint(1000,9999)}")
    if settings.MQTT_USERNAME:
        mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    try:
        mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info("mqtt_connected")
    except Exception as e:
        logger.error("mqtt_connection_failed", error=str(e))

def generate_traffic_data(zone: str, mode: str):
    sensor_id = f"TRAFFIC-{zone}-{random.randint(1, 10):03d}"
    
    base_count = 20
    if mode == "heavy":
        base_count = 80
    elif mode == "critical":
        base_count = 120
        
    hour = datetime.now().hour
    if mode == "normal":
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            base_count = 60
        elif hour < 5 or hour > 22:
            base_count = 5
            
    vehicle_count = max(0, int(random.gauss(base_count, base_count * 0.2)))
    average_speed = max(0, 60 - (vehicle_count * 0.4)) + random.uniform(-5, 5)
    lane_count = 4
    
    occupancy = []
    for _ in range(lane_count):
        occ = min(1.0, max(0.0, (vehicle_count / 150.0) + random.uniform(-0.1, 0.1)))
        occupancy.append(round(occ, 2))
        
    return {
        "sensor_id": sensor_id,
        "zone_id": zone,
        "vehicle_count": vehicle_count,
        "average_speed": round(average_speed, 2),
        "lane_count": lane_count,
        "lane_occupancy": occupancy,
        "timestamp": datetime.utcnow().isoformat()
    }

async def simulation_loop():
    zones = ["ZONE-A", "ZONE-B", "ZONE-C"]
    
    while state.running:
        try:
            target_zones = [state.zone] if state.zone != "all" else zones
            if state.forced_zone and state.forced_zone in zones:
                target_zones = [state.forced_zone]
                
            mode_to_use = state.forced_mode if state.forced_mode else state.mode
            
            for zone in target_zones:
                data = generate_traffic_data(zone, mode_to_use)
                topic = f"city/traffic/{zone}"
                
                if mqtt_client and mqtt_client.is_connected():
                    mqtt_client.publish(topic, json.dumps(data))
                    logger.debug("published_traffic", zone=zone, mode=mode_to_use)
                    
            await asyncio.sleep(1.0 / state.rate)
            
        except Exception as e:
            logger.error("simulation_error", error=str(e))
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup():
    init_mqtt()
    asyncio.create_task(simulation_loop())

@app.on_event("shutdown")
async def shutdown():
    state.running = False
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

@app.post("/control/mode")
def set_mode(mode: str):
    if mode not in ["normal", "heavy", "critical"]:
        return {"error": "Invalid mode"}
    state.mode = mode
    state.forced_mode = None
    return {"status": "success", "mode": mode}

@app.post("/control/trigger-congestion")
def trigger_congestion(zone: str):
    state.forced_zone = zone
    state.forced_mode = "heavy"
    return {"status": "success", "zone": zone, "mode": "heavy"}

@app.post("/control/trigger-critical")
def trigger_critical(zone: str):
    state.forced_zone = zone
    state.forced_mode = "critical"
    return {"status": "success", "zone": zone, "mode": "critical"}

@app.get("/status")
def get_status():
    return {
        "mode": state.mode,
        "rate": state.rate,
        "zone": state.zone,
        "forced_zone": state.forced_zone,
        "forced_mode": state.forced_mode
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ok"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=2.0)
    parser.add_argument("--zone", type=str, default="all")
    parser.add_argument("--mode", type=str, default="normal")
    args = parser.parse_args()
    
    state.rate = args.rate
    state.zone = args.zone
    state.mode = args.mode
    
    uvicorn.run(app, host="0.0.0.0", port=8010)
""",
    "environment-simulator/requirements.txt": """paho-mqtt==2.1.0
structlog==24.4.0
""",
    "environment-simulator/Dockerfile": """FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
""",
    "environment-simulator/main.py": """import argparse
import random
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import structlog
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logger = structlog.get_logger()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "admin")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "admin")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/health', '/ready']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8012), HealthCheckHandler)
    server.serve_forever()

def generate_environment_data(zone: str):
    sensor_id = f"ENV-{zone}-{random.randint(1, 5):03d}"
    
    hour = datetime.now().hour
    base_temp = 20
    if 10 <= hour <= 16:
        base_temp = 30
    elif hour < 6 or hour > 20:
        base_temp = 15
        
    temp = random.gauss(base_temp, 2.0)
    humidity = random.uniform(30.0, 90.0)
    aqi = random.uniform(20.0, 150.0)
    
    if random.random() < 0.05:
        aqi = random.uniform(150.0, 400.0)
        
    return {
        "sensor_id": sensor_id,
        "zone_id": zone,
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2),
        "aqi": round(aqi, 2),
        "pm25": round(aqi * 0.4, 2),
        "pm10": round(aqi * 0.6, 2),
        "co2": round(random.uniform(400, 1000), 2),
        "no2": round(random.uniform(10, 50), 2),
        "wind_speed": round(random.uniform(0, 20), 2),
        "wind_direction": round(random.uniform(0, 360), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=1.0)
    parser.add_argument("--zone", type=str, default="all")
    args = parser.parse_args()
    
    threading.Thread(target=run_health_server, daemon=True).start()
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"env-sim-{random.randint(1000,9999)}")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    zones = ["ZONE-A", "ZONE-B", "ZONE-C"]
    
    try:
        while True:
            target_zones = [args.zone] if args.zone != "all" else zones
            for zone in target_zones:
                data = generate_environment_data(zone)
                client.publish(f"city/environment/{zone}", json.dumps(data))
                logger.debug("published_env", zone=zone)
                
            time.sleep(1.0 / args.rate)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
""",
    "emergency-simulator/requirements.txt": """fastapi==0.115.0
uvicorn==0.30.6
paho-mqtt==2.1.0
structlog==24.4.0
pydantic==2.9.2
""",
    "emergency-simulator/Dockerfile": """FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
""",
    "emergency-simulator/main.py": """import asyncio
import argparse
import random
import json
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import paho.mqtt.client as mqtt
import structlog
import os

logger = structlog.get_logger()
app = FastAPI(title="Emergency Simulator")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "admin")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "admin")

mqtt_client = None
active_emergencies = []

def init_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"emergency-sim-{random.randint(1000,9999)}")
    if MQTT_USERNAME:
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info("mqtt_connected")
    except Exception as e:
        logger.error("mqtt_connection_failed", error=str(e))

@app.on_event("startup")
async def startup():
    init_mqtt()

@app.on_event("shutdown")
async def shutdown():
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

@app.post("/trigger")
def trigger_emergency(zone_id: str, type: str = "ACCIDENT", severity: str = "HIGH"):
    event = {
        "sensor_id": f"EMERGENCY-SYS-{random.randint(10, 99)}",
        "zone_id": zone_id,
        "emergency_type": type,
        "severity": severity,
        "location": {
            "lat": random.uniform(40.0, 41.0),
            "lon": random.uniform(-74.0, -73.0)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if mqtt_client and mqtt_client.is_connected():
        mqtt_client.publish(f"city/emergency/{zone_id}", json.dumps(event))
        active_emergencies.append(event)
        return {"status": "triggered", "event": event}
    return {"error": "MQTT not connected"}

@app.get("/active")
def get_active():
    return {"active": active_emergencies}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ok"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=0.0)
    parser.add_argument("--zone", type=str, default="all")
    args = parser.parse_args()
    
    uvicorn.run(app, host="0.0.0.0", port=8011)
""",
    "camera-simulator/requirements.txt": """paho-mqtt==2.1.0
structlog==24.4.0
""",
    "camera-simulator/Dockerfile": """FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
""",
    "camera-simulator/main.py": """import argparse
import random
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import structlog
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logger = structlog.get_logger()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "admin")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "admin")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/health', '/ready']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8013), HealthCheckHandler)
    server.serve_forever()

def generate_camera_data(zone: str):
    camera_id = f"CAM-{zone}-{random.randint(1, 10):03d}"
    
    incident = random.random() < 0.05
    types = ["ACCIDENT", "FIRE", "CONGESTION"] if incident else [None]
    
    return {
        "camera_id": camera_id,
        "zone_id": zone,
        "vehicle_count": random.randint(5, 50),
        "pedestrian_count": random.randint(0, 20),
        "incident_detected": incident,
        "incident_type": random.choice(types),
        "confidence": round(random.uniform(0.7, 0.99), 2) if incident else 0.95,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=1.0)
    parser.add_argument("--zone", type=str, default="all")
    args = parser.parse_args()
    
    threading.Thread(target=run_health_server, daemon=True).start()
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"camera-sim-{random.randint(1000,9999)}")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    zones = ["ZONE-A", "ZONE-B", "ZONE-C"]
    
    try:
        while True:
            target_zones = [args.zone] if args.zone != "all" else zones
            for zone in target_zones:
                data = generate_camera_data(zone)
                client.publish(f"city/camera/{zone}", json.dumps(data))
                logger.debug("published_camera", zone=zone)
                
            time.sleep(1.0 / args.rate)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
print("done")
