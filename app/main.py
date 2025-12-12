from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.middleware import (
    limiter,
    security_headers_middleware,
    request_logging_middleware,
    trusted_hosts_middleware,
    rate_limit_handler
)
# Import routers
from app.routers import users, posts, auth, admin
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Haikudo Backend API",
    description="A FastAPI backend for Haikudo application with enhanced security",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_handler)

# Add security headers middleware
app.middleware("http")(security_headers_middleware)

# Add request logging middleware
app.middleware("http")(request_logging_middleware)

# Add trusted hosts middleware (only in production)
if not settings.debug:
    app.middleware("http")(trusted_hosts_middleware)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)

# Add trusted host middleware (alternative approach)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.trusted_hosts
    )

# Include routers
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Welcome to Haikudo Backend API"}


@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {
        "status": "healthy", 
        "service": "haikudo-backend",
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production"
    }


@app.get("/api/v1/test-db")
@limiter.limit("5/minute")
async def test_database(request: Request, db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "Database connection successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )


@app.get("/api/v1/info")
@limiter.limit("10/minute") 
async def api_info(request: Request):
    """Get API information and available endpoints"""
    return {
        "api_name": "Haikudo Backend API",
        "version": "1.0.0",
        "description": "A secure FastAPI backend with PostgreSQL",
        "endpoints": {
            "health": "/health",
            "database_test": "/api/v1/test-db",
            "api_info": "/api/v1/info",
            "users": "/api/v1/users",
            "posts": "/api/v1/posts",
            "auth": "/api/v1/auth",
            "admin": "/api/v1/admin"
        },
        "security_features": [
            "Rate limiting",
            "Security headers", 
            "Request logging",
            "CORS protection",
            "Trusted hosts (production)",
            "JWT Authentication",
            "Password validation",
            "Input sanitization"
        ],
        "available_routes": [
            "POST /api/v1/users/register - User registration",
            "POST /api/v1/users/login - User login",
            "GET /api/v1/users/profile - Get user profile",
            "PUT /api/v1/users/profile - Update user profile",
            "GET /api/v1/users - List users",
            "POST /api/v1/posts - Create post",
            "GET /api/v1/posts - List posts",
            "GET /api/v1/posts/{id} - Get specific post",
            "PUT /api/v1/posts/{id} - Update post",
            "DELETE /api/v1/posts/{id} - Delete post",
            "POST /api/v1/auth/forgot-password - Password reset",
            "GET /api/v1/admin/stats - System statistics"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
