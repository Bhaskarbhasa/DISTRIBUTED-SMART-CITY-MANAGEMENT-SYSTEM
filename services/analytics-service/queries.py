from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_traffic_summary():
    # Placeholder for actual DB query
    return {"total_vehicles": 10000, "avg_speed": 45.5, "congestion_level": "MODERATE"}

async def get_zone_analytics(zone_id: str):
    return {"zone_id": zone_id, "vehicle_count": 500, "avg_speed": 40.0}

async def get_hourly_traffic():
    return [{"hour": i, "volume": i * 100} for i in range(24)]

async def get_congestion_distribution():
    return {"LOW": 40, "MODERATE": 30, "HIGH": 20, "SEVERE": 10}

async def get_environment_trends():
    return [{"timestamp": "2023-01-01T00:00:00Z", "aqi": 50, "temp": 22.0}]

async def get_node_health():
    return [{"node_id": "fog-1", "status": "healthy", "uptime": 99.9}]
