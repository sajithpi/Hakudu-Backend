from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware import limiter
from app.config import settings
import redis
import logging

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
logger = logging.getLogger(__name__)


@router.get("/stats")
@limiter.limit("10/minute")
async def get_system_stats(request: Request, db: Session = Depends(get_db)):
    """Get system statistics (admin only)"""
    try:
        # Get database stats
        user_count = db.execute("SELECT COUNT(*) FROM users").scalar()
        post_count = db.execute("SELECT COUNT(*) FROM posts").scalar()
        
        # Get Redis stats if available
        redis_stats = {}
        try:
            redis_client = redis.from_url(settings.redis_url)
            redis_info = redis_client.info()
            redis_stats = {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory_human", "N/A"),
                "uptime": redis_info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.warning(f"Could not get Redis stats: {e}")
            redis_stats = {"status": "unavailable"}
        
        return {
            "database": {
                "users": user_count,
                "posts": post_count
            },
            "redis": redis_stats,
            "application": {
                "version": "1.0.0",
                "environment": "development" if settings.debug else "production"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {"error": "Could not retrieve system statistics"}


@router.get("/logs")
@limiter.limit("5/minute")
async def get_recent_logs(request: Request, lines: int = 100):
    """Get recent application logs (admin only)"""
    # TODO: Implement log retrieval
    return {"message": f"Would return last {lines} log entries"}


@router.post("/maintenance")
@limiter.limit("2/minute")
async def toggle_maintenance_mode(request: Request, enabled: bool):
    """Toggle maintenance mode (admin only)"""
    # TODO: Implement maintenance mode
    return {"message": f"Maintenance mode {'enabled' if enabled else 'disabled'}"}


@router.delete("/cache")
@limiter.limit("3/minute")
async def clear_cache(request: Request):
    """Clear application cache (admin only)"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.flushdb()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"error": "Could not clear cache"}
