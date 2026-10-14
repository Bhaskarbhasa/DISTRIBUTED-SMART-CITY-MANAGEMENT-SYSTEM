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

MQTT_BROKER = os.getenv("MQTT_BROKER") or os.getenv("MQTT_BROKER_HOST") or "mosquitto"
MQTT_PORT = int(os.getenv("MQTT_PORT") or os.getenv("MQTT_BROKER_PORT") or "1883")
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
