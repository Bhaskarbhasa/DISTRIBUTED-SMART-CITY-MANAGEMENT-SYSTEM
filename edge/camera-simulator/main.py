import argparse
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
