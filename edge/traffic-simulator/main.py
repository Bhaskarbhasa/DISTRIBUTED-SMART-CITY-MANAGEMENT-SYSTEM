import asyncio
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
