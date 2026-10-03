import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Inject correlation ID into request state
        request.state.correlation_id = correlation_id
        
        # Bind correlation ID to logger for this request context (if using structlog context vars)
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        # Log request start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        response = await call_next(request)
        
        # Ensure it's in the response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
