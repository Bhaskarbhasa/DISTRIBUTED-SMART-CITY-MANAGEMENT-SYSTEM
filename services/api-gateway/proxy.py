import httpx
from fastapi import Request, Response, HTTPException
import structlog
from config import settings

logger = structlog.get_logger()

# Shared async client for proxying
client = httpx.AsyncClient(timeout=settings.proxy_timeout)

async def proxy_request(request: Request, target_url: str) -> Response:
    path = request.url.path
    if path.startswith("/api"):
        path = path[4:]
        
    query = request.url.query.encode("utf-8")
    
    # Construct the full target URL
    url = f"{target_url}{path}"
    if query:
        url += f"?{query.decode('utf-8')}"
        
    # Forward headers but remove host to avoid SNI/Host mismatch issues
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Read the request body
    body = await request.body()
    
    logger.info("proxying_request", target_url=url, method=request.method)
    
    try:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )
    except httpx.RequestError as exc:
        logger.error("proxy_request_failed", error=str(exc), target_url=url)
        raise HTTPException(status_code=502, detail=f"Bad Gateway: Unable to reach upstream service at {url}")
        
    # Build FastAPI response from httpx response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
