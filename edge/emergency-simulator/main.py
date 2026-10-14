import asyncio
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

MQTT_BROKER = os.getenv("MQTT_BROKER") or os.getenv("MQTT_BROKER_HOST") or "mosquitto"
MQTT_PORT = int(os.getenv("MQTT_PORT") or os.getenv("MQTT_BROKER_PORT") or "1883")
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
