from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
import structlog
from config import settings

logger = structlog.get_logger()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/health",
            "/ready",
            "/api/services",
            "/docs",
            "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        if any(path.startswith(p) for p in self.exempt_paths):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("auth_failed", reason="missing_or_invalid_header", path=path)
            return JSONResponse(status_code=401, content={"detail": "Unauthorized: Missing or invalid token"})
            
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            
            # Create a mutable copy of the headers
            mutable_headers = dict(request.scope["headers"])
            
            # Inject user info
            user_id = str(payload.get("sub", ""))
            user_role = str(payload.get("role", "user"))
            user_email = str(payload.get("email", ""))
            
            mutable_headers[b"x-user-id"] = user_id.encode()
            mutable_headers[b"x-user-role"] = user_role.encode()
            mutable_headers[b"x-user-email"] = user_email.encode()
            
            # Update request scope headers
            request.scope["headers"] = [(k, v) for k, v in mutable_headers.items()]
            
            # Add to state as well
            request.state.user_id = user_id
            request.state.user_role = user_role
            
        except JWTError as e:
            logger.warning("auth_failed", reason="invalid_token", error=str(e), path=path)
            return JSONResponse(status_code=401, content={"detail": "Unauthorized: Invalid or expired token"})
            
        return await call_next(request)
