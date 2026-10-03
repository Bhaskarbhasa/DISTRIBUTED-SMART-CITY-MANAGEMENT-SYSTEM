import redis.asyncio as redis
import json
from config import settings
from models import EnvironmentTelemetry, EnvironmentAlert
from typing import List, Dict, Optional

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def cache_telemetry(telemetry: EnvironmentTelemetry):
    key = f"env:zone:{telemetry.zone_id}:latest"
    await redis_client.set(key, telemetry.model_dump_json())
    
    # History (last 100)
    history_key = f"env:zone:{telemetry.zone_id}:history"
    await redis_client.lpush(history_key, telemetry.model_dump_json())
    await redis_client.ltrim(history_key, 0, 99)

async def cache_alert(alert: EnvironmentAlert):
    key = f"env:alert:{alert.alert_id}"
    await redis_client.setex(key, 86400, alert.model_dump_json()) # 24h
    
    # Active alerts list
    active_key = f"env:zone:{alert.zone_id}:active_alerts"
    await redis_client.sadd(active_key, alert.alert_id)

async def get_latest_zones() -> Dict:
    keys = await redis_client.keys("env:zone:*:latest")
    res = {}
    for k in keys:
        zone_id = k.split(":")[2]
        val = await redis_client.get(k)
        if val:
            res[zone_id] = json.loads(val)
    return res

async def get_zone_details(zone_id: str) -> Optional[Dict]:
    val = await redis_client.get(f"env:zone:{zone_id}:latest")
    return json.loads(val) if val else None

async def get_zone_history(zone_id: str, limit: int = 10) -> List[Dict]:
    vals = await redis_client.lrange(f"env:zone:{zone_id}:history", 0, limit - 1)
    return [json.loads(v) for v in vals]

async def get_active_alerts() -> List[Dict]:
    keys = await redis_client.keys("env:alert:*")
    alerts = []
    for k in keys:
        val = await redis_client.get(k)
        if val:
            alerts.append(json.loads(val))
    return alerts
