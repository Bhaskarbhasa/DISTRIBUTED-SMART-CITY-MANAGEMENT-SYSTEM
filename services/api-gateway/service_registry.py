import httpx
import structlog
from typing import Dict, Any
from config import settings

logger = structlog.get_logger()

SERVICES = {
    "auth-service": settings.auth_service_url,
    "traffic-service": settings.traffic_service_url,
    "emergency-service": settings.emergency_service_url,
    "environment-service": settings.environment_service_url,
    "analytics-service": settings.analytics_service_url,
    "ingestion-service": settings.ingestion_service_url,
    "fog-node": settings.fog_node_service_url,
}

async def get_services_health() -> Dict[str, Any]:
    health_status = {}
    
    async with httpx.AsyncClient(timeout=2.0) as client:
        for name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    health_status[name] = {"status": "healthy", "url": url}
                else:
                    health_status[name] = {"status": "unhealthy", "code": response.status_code, "url": url}
            except Exception as e:
                health_status[name] = {"status": "down", "error": str(e), "url": url}
                logger.error("service_health_check_failed", service=name, error=str(e))
                
    return health_status
