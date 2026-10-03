import redis.asyncio as redis
import json
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def set_traffic_state(zone_id: str, state: dict):
    await redis_client.setex(f"traffic:state:{zone_id}", 300, json.dumps(state))

async def get_traffic_state(zone_id: str):
    data = await redis_client.get(f"traffic:state:{zone_id}")
    return json.loads(data) if data else None

async def get_all_zones_state():
    keys = await redis_client.keys("traffic:state:*")
    states = []
    for key in keys:
        data = await redis_client.get(key)
        if data:
            states.append(json.loads(data))
    return states

async def set_signal_state(zone_id: str, state: dict):
    await redis_client.setex(f"traffic:signal:{zone_id}", 300, json.dumps(state))

async def get_signal_state(zone_id: str):
    data = await redis_client.get(f"traffic:signal:{zone_id}")
    return json.loads(data) if data else None

async def get_all_signals_state():
    keys = await redis_client.keys("traffic:signal:*")
    states = []
    for key in keys:
        data = await redis_client.get(key)
        if data:
            states.append(json.loads(data))
    return states
