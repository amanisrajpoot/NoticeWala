"""
Personalization API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.personalization_service import personalization_service
from app.schemas.personalization import (
    UserInteraction,
    RecommendationRequest,
    RecommendationResponse,
    UserProfileResponse,
    PreferenceUpdate
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/interaction")
async def record_user_interaction(
    interaction: UserInteraction,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Record user interaction for preference learning"""
    
    try:
        result = await personalization_service.learn_user_preferences(
            user_id=current_user_id,
            interaction_type=interaction.interaction_type,
            announcement_id=interaction.announcement_id,
            db=db
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Interaction recorded successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to record interaction")
            )
        
    except Exception as e:
        logger.error(f"Failed to record user interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record interaction: {str(e)}"
        )


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100),
    recommendation_type: str = Query("personalized", regex="^(personalized|content_based|collaborative)$"),
    content_id: Optional[str] = Query(None, description="Required for content_based recommendations"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for the user"""
    
    try:
        if recommendation_type == "personalized":
            recommendations = await personalization_service.get_personalized_recommendations(
                user_id=current_user_id,
                limit=limit,
                db=db
            )
        elif recommendation_type == "content_based":
            if not content_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="content_id is required for content_based recommendations"
                )
            recommendations = await personalization_service.get_content_based_recommendations(
                user_id=current_user_id,
                content_id=content_id,
                limit=limit,
                db=db
            )
        elif recommendation_type == "collaborative":
            recommendations = await personalization_service.get_collaborative_recommendations(
                user_id=current_user_id,
                limit=limit,
                db=db
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recommendation_type"
            )
        
        return RecommendationResponse(
            success=True,
            recommendations=recommendations,
            recommendation_type=recommendation_type,
            total_count=len(recommendations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get personalized recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get user personalization profile"""
    
    try:
        profile = await personalization_service._get_user_profile(current_user_id, db)
        
        return UserProfileResponse(
            success=True,
            profile=profile,
            user_id=current_user_id
        )
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/preferences")
async def update_user_preferences(
    preference_update: PreferenceUpdate,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Update user preferences manually"""
    
    try:
        # Get current profile
        profile = await personalization_service._get_user_profile(current_user_id, db)
        
        # Update preferences
        if preference_update.categories is not None:
            profile["preferences"]["categories"] = preference_update.categories
        
        if preference_update.exam_types is not None:
            profile["preferences"]["exam_types"] = preference_update.exam_types
        
        if preference_update.locations is not None:
            profile["preferences"]["locations"] = preference_update.locations
        
        if preference_update.keywords is not None:
            profile["preferences"]["keywords"] = preference_update.keywords
        
        if preference_update.difficulty_levels is not None:
            profile["preferences"]["difficulty_levels"] = preference_update.difficulty_levels
        
        # Save updated profile
        await personalization_service._save_user_profile(current_user_id, profile, db)
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "updated_preferences": preference_update.dict(exclude_unset=True)
        }
        
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/similar-users")
async def get_similar_users(
    limit: int = Query(10, ge=1, le=50),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get users with similar preferences"""
    
    try:
        similar_users = await personalization_service._find_similar_users(
            user_id=current_user_id,
            db=db
        )
        
        return {
            "success": True,
            "similar_users": similar_users[:limit],
            "total_count": len(similar_users)
        }
        
    except Exception as e:
        logger.error(f"Failed to get similar users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get similar users: {str(e)}"
        )


@router.get("/insights")
async def get_personalization_insights(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get personalization insights for the user"""
    
    try:
        profile = await personalization_service._get_user_profile(current_user_id, db)
        
        # Calculate insights
        insights = {
            "total_interactions": len(profile.get("interactions", [])),
            "preferred_categories": sorted(
                profile.get("preference_scores", {}).get("categories", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "preferred_exam_types": sorted(
                profile.get("preference_scores", {}).get("exam_types", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "preferred_locations": sorted(
                profile.get("preference_scores", {}).get("locations", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "preferred_keywords": sorted(
                profile.get("preference_scores", {}).get("keywords", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "behavioral_patterns": profile.get("behavioral_patterns", {}),
            "last_updated": profile.get("last_updated")
        }
        
        return {
            "success": True,
            "insights": insights,
            "user_id": current_user_id
        }
        
    except Exception as e:
        logger.error(f"Failed to get personalization insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )


@router.delete("/profile")
async def reset_user_profile(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Reset user profile to default settings"""
    
    try:
        # Create default profile
        default_profile = personalization_service._create_default_profile()
        
        # Save default profile
        await personalization_service._save_user_profile(current_user_id, default_profile, db)
        
        return {
            "success": True,
            "message": "User profile reset to default settings"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset profile: {str(e)}"
        )


@router.get("/recommendation-explanations")
async def get_recommendation_explanations(
    announcement_id: str,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get explanation for why a specific announcement was recommended"""
    
    try:
        from app.models.announcement import Announcement
        
        # Get the announcement
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Get user profile
        profile = await personalization_service._get_user_profile(current_user_id, db)
        
        # Get recommendation reasons
        reasons = await personalization_service._get_recommendation_reasons(
            profile, announcement
        )
        
        # Calculate recommendation score
        score = await personalization_service._calculate_recommendation_score(
            profile, announcement, db
        )
        
        return {
            "success": True,
            "announcement_id": announcement_id,
            "recommendation_score": score,
            "reasons": reasons,
            "explanation": f"This announcement was recommended because: {'; '.join(reasons) if reasons else 'No specific reasons found'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recommendation explanations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get explanations: {str(e)}"
        )
