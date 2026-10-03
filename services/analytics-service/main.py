from fastapi import FastAPI
from prometheus_client import make_asgi_app
import queries
import predictions
import minio_client
from config import settings

app = FastAPI(title="Analytics Service")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/analytics/traffic/summary")
async def get_traffic_summary():
    return await queries.get_traffic_summary()

@app.get("/analytics/traffic/zones/{zone_id}")
async def get_traffic_zone(zone_id: str):
    return await queries.get_zone_analytics(zone_id)

@app.get("/analytics/traffic/hourly")
async def get_traffic_hourly():
    return await queries.get_hourly_traffic()

@app.get("/analytics/traffic/congestion-distribution")
async def get_congestion_dist():
    return await queries.get_congestion_distribution()

@app.get("/analytics/environment/trends")
async def get_env_trends():
    return await queries.get_environment_trends()

@app.get("/analytics/system/throughput")
async def get_throughput():
    # Mock
    return {"events_per_second": 1500, "bytes_per_second": 1024 * 1024}

@app.get("/analytics/system/latency")
async def get_latency():
    # Mock
    return {"avg_latency_ms": 45.2, "p99_latency_ms": 120.5}

@app.get("/analytics/system/node-health")
async def get_node_health():
    return await queries.get_node_health()

@app.get("/analytics/predictions/traffic/{zone_id}")
async def get_prediction(zone_id: str):
    return predictions.predict_traffic(zone_id)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}
