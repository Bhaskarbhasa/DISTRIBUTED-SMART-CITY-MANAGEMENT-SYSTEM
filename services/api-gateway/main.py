from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog
import asyncio
import websockets

from config import settings
from proxy import proxy_request
from service_registry import get_services_health
from middleware.correlation import CorrelationIdMiddleware
from middleware.auth_middleware import AuthMiddleware
from middleware.rate_limiter import limiter, get_rate_limit, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = structlog.get_logger()

app = FastAPI(title="Smart City API Gateway", version="1.0.0")

# Setup metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Setup Slowapi rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

@app.get("/api/services")
@limiter.limit("1000/minute")
async def list_services(request: Request):
    return await get_services_health()

# Routing HTTP traffic to backends
ROUTE_MAP = {
    "/api/auth": settings.auth_service_url,
    "/api/traffic": settings.traffic_service_url,
    "/api/emergency": settings.emergency_service_url,
    "/api/environment": settings.environment_service_url,
    "/api/analytics": settings.analytics_service_url,
    "/api/nodes": settings.fog_node_service_url,
    "/api/devices": settings.ingestion_service_url,
}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@limiter.limit("1000/minute")
async def route_all(request: Request, path: str):
    # Match route prefix
    target_url = None
    for prefix, url in ROUTE_MAP.items():
        if request.url.path.startswith(prefix):
            target_url = url
            break
            
    if not target_url:
        raise HTTPException(status_code=404, detail="Route not found in API Gateway")
        
    return await proxy_request(request, target_url)


# WebSocket proxies
async def proxy_websocket(websocket: WebSocket, target_ws_url: str):
    await websocket.accept()
    logger.info("websocket_proxy_started", target=target_ws_url)
    
    try:
        async with websockets.connect(target_ws_url) as backend_ws:
            async def forward_to_backend():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await backend_ws.send(data)
                except WebSocketDisconnect:
                    logger.info("client_ws_disconnected")
                except Exception as e:
                    logger.error("ws_forward_to_backend_error", error=str(e))
                    
            async def forward_to_client():
                try:
                    while True:
                        data = await backend_ws.recv()
                        await websocket.send_text(data)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("backend_ws_disconnected")
                except Exception as e:
                    logger.error("ws_forward_to_client_error", error=str(e))

            await asyncio.gather(
                forward_to_backend(),
                forward_to_client()
            )
    except Exception as e:
        logger.error("ws_connection_failed", target=target_ws_url, error=str(e))
        await websocket.close(code=1011)

@app.websocket("/ws/traffic")
async def ws_traffic(websocket: WebSocket):
    # Convert HTTP URL to WS URL
    ws_url = settings.traffic_service_url.replace("http://", "ws://").replace("https://", "wss://")
    await proxy_websocket(websocket, f"{ws_url}/ws/traffic")

@app.websocket("/ws/emergency")
async def ws_emergency(websocket: WebSocket):
    ws_url = settings.emergency_service_url.replace("http://", "ws://").replace("https://", "wss://")
    await proxy_websocket(websocket, f"{ws_url}/ws/emergency")
