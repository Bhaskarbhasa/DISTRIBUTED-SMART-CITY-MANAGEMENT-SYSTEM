from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Use client IP as the key for rate limiting
limiter = Limiter(key_func=get_remote_address)

def get_rate_limit(request: Request) -> str:
    # 1000 req/min for device ingestion routes
    if request.url.path.startswith("/api/devices"):
        return "1000/minute"
    # 100 req/min for regular users
    return "100/minute"
