import redis.asyncio as redis
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def is_duplicate(event_id: str) -> bool:
    key = f"emergency:dedup:{event_id}"
    exists = await redis_client.get(key)
    if exists:
        return True
    await redis_client.setex(key, 86400, "1") # 24h retention
    return False
