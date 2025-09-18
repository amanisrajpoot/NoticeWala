"""
Analytics API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.analytics_service import analytics_service
from app.schemas.analytics import (
    UserInteractionTrack,
    UserAnalyticsResponse,
    SystemAnalyticsResponse,
    ContentAnalyticsResponse,
    RecommendationAnalyticsResponse
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/track-interaction")
async def track_user_interaction(
    interaction: UserInteractionTrack,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Track user interaction for analytics"""
    
    try:
        result = await analytics_service.track_user_interaction(
            user_id=current_user_id,
            interaction_type=interaction.interaction_type,
            announcement_id=interaction.announcement_id,
            metadata=interaction.metadata,
            db=db
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Interaction tracked successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to track interaction")
            )
        
    except Exception as e:
        logger.error(f"Failed to track user interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track interaction: {str(e)}"
        )


@router.get("/user", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for the current user"""
    
    try:
        analytics = await analytics_service.get_user_analytics(
            user_id=current_user_id,
            days=days,
            db=db
        )
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analytics["error"]
            )
        
        return UserAnalyticsResponse(
            success=True,
            analytics=analytics,
            user_id=current_user_id,
            period_days=days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.get("/system", response_model=SystemAnalyticsResponse)
async def get_system_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get system-wide analytics and insights"""
    
    try:
        analytics = await analytics_service.get_system_analytics(
            days=days,
            db=db
        )
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )
        
        return SystemAnalyticsResponse(
            success=True,
            analytics=analytics,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Failed to get system analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system analytics: {str(e)}"
        )


@router.get("/content", response_model=ContentAnalyticsResponse)
async def get_content_analytics(
    content_id: Optional[str] = Query(None, description="Specific content ID to analyze"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get analytics for specific content or content trends"""
    
    try:
        analytics = await analytics_service.get_content_analytics(
            content_id=content_id,
            days=days,
            db=db
        )
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=analytics["error"]
            )
        
        return ContentAnalyticsResponse(
            success=True,
            analytics=analytics,
            content_id=content_id,
            period_days=days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get content analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content analytics: {str(e)}"
        )


@router.get("/recommendations", response_model=RecommendationAnalyticsResponse)
async def get_recommendation_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get analytics for recommendation system performance"""
    
    try:
        analytics = await analytics_service.get_recommendation_analytics(
            user_id=current_user_id,
            days=days,
            db=db
        )
        
        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )
        
        return RecommendationAnalyticsResponse(
            success=True,
            analytics=analytics,
            user_id=current_user_id,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"Failed to get recommendation analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendation analytics: {str(e)}"
        )


@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard data"""
    
    try:
        # Get user analytics
        user_analytics = await analytics_service.get_user_analytics(
            user_id=current_user_id,
            days=days,
            db=db
        )
        
        # Get system analytics
        system_analytics = await analytics_service.get_system_analytics(
            days=days,
            db=db
        )
        
        # Get recommendation analytics
        recommendation_analytics = await analytics_service.get_recommendation_analytics(
            user_id=current_user_id,
            days=days,
            db=db
        )
        
        dashboard = {
            "user_analytics": user_analytics,
            "system_analytics": system_analytics,
            "recommendation_analytics": recommendation_analytics,
            "summary": {
                "user_engagement_score": user_analytics.get("engagement_metrics", {}).get("engagement_score", 0),
                "system_health_score": 95.0,  # Mock system health
                "recommendation_accuracy": recommendation_analytics.get("recommendation_metrics", {}).get("recommendation_accuracy", 0),
                "total_users": system_analytics.get("user_metrics", {}).get("total_users", 0),
                "active_users": system_analytics.get("user_metrics", {}).get("active_users", 0)
            }
        }
        
        return {
            "success": True,
            "dashboard": dashboard,
            "period_days": days,
            "generated_at": user_analytics.get("generated_at")
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics dashboard: {str(e)}"
        )


@router.get("/insights")
async def get_analytics_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    insight_type: str = Query("all", description="Type of insights: all, user, system, content, recommendations"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get analytics insights and recommendations"""
    
    try:
        insights = []
        
        if insight_type in ["all", "user"]:
            user_analytics = await analytics_service.get_user_analytics(
                user_id=current_user_id,
                days=days,
                db=db
            )
            
            # Generate user insights
            user_insights = await _generate_user_insights(user_analytics)
            insights.extend(user_insights)
        
        if insight_type in ["all", "system"]:
            system_analytics = await analytics_service.get_system_analytics(
                days=days,
                db=db
            )
            
            # Generate system insights
            system_insights = await _generate_system_insights(system_analytics)
            insights.extend(system_insights)
        
        if insight_type in ["all", "recommendations"]:
            recommendation_analytics = await analytics_service.get_recommendation_analytics(
                user_id=current_user_id,
                days=days,
                db=db
            )
            
            # Generate recommendation insights
            recommendation_insights = await _generate_recommendation_insights(recommendation_analytics)
            insights.extend(recommendation_insights)
        
        return {
            "success": True,
            "insights": insights,
            "insight_type": insight_type,
            "period_days": days,
            "total_insights": len(insights)
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics insights: {str(e)}"
        )


@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", description="Export format: json, csv"),
    days: int = Query(30, ge=1, le=365, description="Number of days to export"),
    data_type: str = Query("user", description="Type of data to export: user, system, content"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Export analytics data in specified format"""
    
    try:
        if data_type == "user":
            data = await analytics_service.get_user_analytics(
                user_id=current_user_id,
                days=days,
                db=db
            )
        elif data_type == "system":
            data = await analytics_service.get_system_analytics(
                days=days,
                db=db
            )
        elif data_type == "content":
            data = await analytics_service.get_content_analytics(
                days=days,
                db=db
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data_type. Must be user, system, or content"
            )
        
        if format == "json":
            return {
                "success": True,
                "data": data,
                "format": "json",
                "exported_at": data.get("generated_at")
            }
        elif format == "csv":
            # In a real implementation, this would convert data to CSV
            return {
                "success": True,
                "message": "CSV export not implemented yet",
                "format": "csv"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Must be json or csv"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export analytics data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


async def _generate_user_insights(user_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate user-specific insights"""
    
    insights = []
    
    # Engagement insights
    engagement = user_analytics.get("engagement_metrics", {})
    if engagement.get("engagement_score", 0) > 0.7:
        insights.append({
            "type": "positive",
            "category": "engagement",
            "title": "High Engagement",
            "description": "You have high engagement with the platform",
            "recommendation": "Keep up the great work!"
        })
    elif engagement.get("engagement_score", 0) < 0.3:
        insights.append({
            "type": "improvement",
            "category": "engagement",
            "title": "Low Engagement",
            "description": "Your engagement could be improved",
            "recommendation": "Try exploring different categories or setting up more subscriptions"
        })
    
    # Content preference insights
    preferences = user_analytics.get("content_preferences", {})
    if preferences.get("preferred_categories"):
        insights.append({
            "type": "info",
            "category": "preferences",
            "title": "Content Preferences",
            "description": f"You're most interested in: {', '.join(preferences['preferred_categories'][:3])}",
            "recommendation": "We'll continue to prioritize this content for you"
        })
    
    return insights


async def _generate_system_insights(system_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate system-wide insights"""
    
    insights = []
    
    # User growth insights
    user_metrics = system_analytics.get("user_metrics", {})
    if user_metrics.get("user_growth_rate", 0) > 0.1:
        insights.append({
            "type": "positive",
            "category": "growth",
            "title": "Strong User Growth",
            "description": f"User base has grown by {user_metrics.get('user_growth_rate', 0)*100:.1f}%",
            "recommendation": "Consider scaling infrastructure"
        })
    
    # Content insights
    content_metrics = system_analytics.get("content_metrics", {})
    if content_metrics.get("content_growth_rate", 0) > 0.05:
        insights.append({
            "type": "info",
            "category": "content",
            "title": "Content Growth",
            "description": "New content is being added regularly",
            "recommendation": "Monitor content quality and relevance"
        })
    
    return insights


async def _generate_recommendation_insights(recommendation_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendation system insights"""
    
    insights = []
    
    # Recommendation accuracy insights
    metrics = recommendation_analytics.get("recommendation_metrics", {})
    accuracy = metrics.get("recommendation_accuracy", 0)
    
    if accuracy > 0.8:
        insights.append({
            "type": "positive",
            "category": "recommendations",
            "title": "High Recommendation Accuracy",
            "description": f"Recommendation accuracy is {accuracy*100:.1f}%",
            "recommendation": "The recommendation system is working well"
        })
    elif accuracy < 0.5:
        insights.append({
            "type": "improvement",
            "category": "recommendations",
            "title": "Low Recommendation Accuracy",
            "description": f"Recommendation accuracy is {accuracy*100:.1f}%",
            "recommendation": "Consider improving the recommendation algorithm"
        })
    
    return insights
