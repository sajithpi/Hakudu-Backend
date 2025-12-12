from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import logging
import uuid
from typing import Callable
import redis
from app.config import settings

# Set up Redis for rate limiting
try:
    redis_client = redis.from_url(settings.redis_url)
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError):
    # Fallback to in-memory rate limiting if Redis is not available
    redis_client = None
    logging.warning("Redis not available, using in-memory rate limiting")

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url if redis_client else "memory://",
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)

# Security headers middleware
async def security_headers_middleware(request: Request, call_next: Callable):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Request logging middleware
async def request_logging_middleware(request: Request, call_next: Callable):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request
    logging.info(
        f"Request {request_id}: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logging.info(
        f"Response {request_id}: {response.status_code} "
        f"processed in {process_time:.3f}s"
    )
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Trusted host middleware
async def trusted_hosts_middleware(request: Request, call_next: Callable):
    host = request.headers.get("host", "").split(":")[0]
    
    if not settings.debug and host not in settings.trusted_hosts:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Untrusted host"}
        )
    
    return await call_next(request)

# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": "60"
        }
    )
    response.headers["Retry-After"] = "60"
    return response

# JWT Bearer token scheme (for future authentication)
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = None):
    """
    Get current user from JWT token.
    This is a placeholder for future authentication implementation.
    """
    if not credentials:
        return None
    
    # TODO: Implement JWT token validation
    # For now, just return None (no authentication)
    return None
