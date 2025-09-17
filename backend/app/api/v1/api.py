"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import announcements, auth, health, users, subscriptions, notifications, crawlers

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router, 
    prefix="/health", 
    tags=["health"]
)

api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"]
)

api_router.include_router(
    announcements.router, 
    prefix="/announcements", 
    tags=["announcements"]
)

api_router.include_router(
    subscriptions.router, 
    prefix="/subscriptions", 
    tags=["subscriptions"]
)

api_router.include_router(
    notifications.router, 
    prefix="/notifications", 
    tags=["notifications"]
)

api_router.include_router(
    crawlers.router, 
    prefix="/crawlers", 
    tags=["crawlers"]
)
