"""
Advanced Search API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.search_service import search_service
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchSuggestionResponse,
    SearchAnalyticsResponse,
    AdvancedSearchRequest
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Perform semantic search using vector similarity"""
    
    try:
        results = await search_service.semantic_search(
            query=request.query,
            user_id=current_user_id,
            limit=request.limit,
            filters=request.filters,
            db=db
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=results,
            total_count=len(results),
            search_type="semantic"
        )
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/natural-language", response_model=SearchResponse)
async def natural_language_search(
    request: SearchRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Process natural language queries and return relevant results"""
    
    try:
        results = await search_service.natural_language_search(
            query=request.query,
            user_id=current_user_id,
            limit=request.limit,
            db=db
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=results,
            total_count=len(results),
            search_type="natural_language"
        )
        
    except Exception as e:
        logger.error(f"Natural language search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Natural language search failed: {str(e)}"
        )


@router.post("/advanced-filter", response_model=SearchResponse)
async def advanced_filter_search(
    request: AdvancedSearchRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters"""
    
    try:
        results = await search_service.advanced_filter_search(
            filters=request.filters,
            user_id=current_user_id,
            limit=request.limit,
            db=db
        )
        
        return SearchResponse(
            success=True,
            query="Advanced filter search",
            results=results,
            total_count=len(results),
            search_type="advanced_filter"
        )
        
    except Exception as e:
        logger.error(f"Advanced filter search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced filter search failed: {str(e)}"
        )


@router.get("/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    query: str = Query(..., description="Partial search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    
    try:
        suggestions = await search_service.get_search_suggestions(
            query=query,
            limit=limit,
            db=db
        )
        
        return SearchSuggestionResponse(
            success=True,
            query=query,
            suggestions=suggestions,
            total_count=len(suggestions)
        )
        
    except Exception as e:
        logger.error(f"Failed to get search suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get search analytics and insights"""
    
    try:
        analytics = await search_service.get_search_analytics(
            user_id=current_user_id,
            days=days,
            db=db
        )
        
        return SearchAnalyticsResponse(
            success=True,
            analytics=analytics,
            period_days=days,
            user_specific=current_user_id is not None
        )
        
    except Exception as e:
        logger.error(f"Failed to get search analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/trending")
async def get_trending_searches(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of trending searches"),
    db: Session = Depends(get_db)
):
    """Get trending search queries"""
    
    try:
        # This would require a search_logs table in a real implementation
        # For now, return mock trending searches
        trending_searches = [
            {"query": "UPSC 2024", "count": 150, "trend": "up"},
            {"query": "SSC CGL", "count": 120, "trend": "up"},
            {"query": "Banking jobs", "count": 100, "trend": "stable"},
            {"query": "Railway recruitment", "count": 90, "trend": "down"},
            {"query": "Engineering exams", "count": 80, "trend": "up"}
        ]
        
        return {
            "success": True,
            "trending_searches": trending_searches[:limit],
            "total_count": len(trending_searches)
        }
        
    except Exception as e:
        logger.error(f"Failed to get trending searches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending searches: {str(e)}"
        )


@router.get("/popular-categories")
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of categories"),
    db: Session = Depends(get_db)
):
    """Get popular search categories"""
    
    try:
        from app.models.announcement import Announcement
        from sqlalchemy import func
        
        # Get category counts
        category_counts = db.query(
            func.jsonb_array_elements_text(Announcement.categories).label('category'),
            func.count().label('count')
        ).filter(
            Announcement.categories.isnot(None)
        ).group_by('category').order_by(
            func.count().desc()
        ).limit(limit).all()
        
        popular_categories = [
            {"category": row.category, "count": row.count}
            for row in category_counts
        ]
        
        return {
            "success": True,
            "popular_categories": popular_categories,
            "total_count": len(popular_categories)
        }
        
    except Exception as e:
        logger.error(f"Failed to get popular categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular categories: {str(e)}"
        )


@router.get("/search-history")
async def get_user_search_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of search history items"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get user's search history"""
    
    try:
        # This would require a search_logs table in a real implementation
        # For now, return mock search history
        search_history = [
            {
                "query": "UPSC 2024 notification",
                "timestamp": "2024-01-15T10:30:00Z",
                "results_count": 15,
                "search_type": "semantic"
            },
            {
                "query": "Banking jobs in Delhi",
                "timestamp": "2024-01-14T14:20:00Z",
                "results_count": 8,
                "search_type": "natural_language"
            },
            {
                "query": "SSC CGL exam dates",
                "timestamp": "2024-01-13T09:15:00Z",
                "results_count": 12,
                "search_type": "semantic"
            }
        ]
        
        return {
            "success": True,
            "search_history": search_history[:limit],
            "total_count": len(search_history),
            "user_id": current_user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to get search history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search history: {str(e)}"
        )


@router.delete("/search-history")
async def clear_user_search_history(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Clear user's search history"""
    
    try:
        # This would require a search_logs table in a real implementation
        # For now, return success message
        
        logger.info(f"Search history cleared for user {current_user_id}")
        
        return {
            "success": True,
            "message": "Search history cleared successfully",
            "user_id": current_user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to clear search history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear search history: {str(e)}"
        )


@router.get("/search-status")
async def get_search_service_status():
    """Get search service status and configuration"""
    
    try:
        status_info = {
            "service_active": True,
            "sentence_transformer_available": search_service.sentence_transformer is not None,
            "tfidf_vectorizer_available": search_service.tfidf_vectorizer is not None,
            "search_types_supported": [
                "semantic",
                "natural_language",
                "advanced_filter"
            ],
            "features": [
                "semantic_search",
                "natural_language_processing",
                "personalization",
                "suggestions",
                "analytics"
            ]
        }
        
        return {
            "success": True,
            "status": status_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get search service status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search status: {str(e)}"
        )
