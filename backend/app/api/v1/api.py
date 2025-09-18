"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import announcements, auth, health, users, subscriptions, notifications, crawlers, ai_processing, personalization, search, analytics, offline_sync, premium

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

api_router.include_router(
    ai_processing.router,
    prefix="/ai",
    tags=["ai-processing"]
)

api_router.include_router(
    personalization.router,
    prefix="/personalization",
    tags=["personalization"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    offline_sync.router,
    prefix="/offline-sync",
    tags=["offline-sync"]
)

api_router.include_router(
    premium.router,
    prefix="/premium",
    tags=["premium"]
)
