from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
import redis
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "NoticeWala API",
        "version": "1.0.0"
    }

@router.get("/health/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Check database connectivity."""
    try:
        # Simple query to test database connection
        result = db.execute("SELECT 1").scalar()
        if result == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/health/redis")
async def redis_health_check():
    """Check Redis connectivity."""
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        result = redis_client.ping()
        if result:
            return {
                "status": "healthy",
                "redis": "connected",
                "message": "Redis connection successful"
            }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}"
        )

@router.get("/health/elasticsearch")
async def elasticsearch_health_check():
    """Check Elasticsearch connectivity."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ELASTICSEARCH_URL}/_cluster/health")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "elasticsearch": "connected",
                    "cluster_status": data.get("status"),
                    "message": "Elasticsearch connection successful"
                }
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Elasticsearch connection failed: {str(e)}"
        )

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for all services."""
    health_status = {
        "status": "healthy",
        "service": "NoticeWala API",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1").scalar()
        health_status["checks"]["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Check Elasticsearch
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ELASTICSEARCH_URL}/_cluster/health")
            if response.status_code == 200:
                data = response.json()
                health_status["checks"]["elasticsearch"] = {
                    "status": "healthy",
                    "cluster_status": data.get("status"),
                    "message": "Connected"
                }
            else:
                health_status["checks"]["elasticsearch"] = {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["elasticsearch"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    return health_status
