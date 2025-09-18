"""
Personalization schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserInteraction(BaseModel):
    """Schema for recording user interactions"""
    interaction_type: str = Field(..., description="Type of interaction: view, click, bookmark, subscribe, dismiss, share, download")
    announcement_id: str = Field(..., description="ID of the announcement interacted with")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the interaction")


class RecommendationRequest(BaseModel):
    """Schema for recommendation requests"""
    limit: int = Field(20, ge=1, le=100, description="Maximum number of recommendations to return")
    recommendation_type: str = Field("personalized", description="Type of recommendation: personalized, content_based, collaborative")
    content_id: Optional[str] = Field(None, description="Content ID for content-based recommendations")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters to apply")


class RecommendationItem(BaseModel):
    """Schema for individual recommendation items"""
    announcement: Dict[str, Any] = Field(..., description="Announcement data")
    score: float = Field(..., description="Recommendation score")
    reasons: List[str] = Field(..., description="Reasons for recommendation")
    similarity_reason: Optional[str] = Field(None, description="Reason for content-based recommendations")


class RecommendationResponse(BaseModel):
    """Schema for recommendation responses"""
    success: bool = Field(..., description="Whether the request was successful")
    recommendations: List[RecommendationItem] = Field(..., description="List of recommendations")
    recommendation_type: str = Field(..., description="Type of recommendations returned")
    total_count: int = Field(..., description="Total number of recommendations")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    categories: List[str] = Field(default_factory=list, description="Preferred exam categories")
    exam_types: List[str] = Field(default_factory=list, description="Preferred exam types")
    locations: List[str] = Field(default_factory=list, description="Preferred locations")
    keywords: List[str] = Field(default_factory=list, description="Preferred keywords")
    difficulty_levels: List[str] = Field(default_factory=list, description="Preferred difficulty levels")
    time_preferences: Dict[str, float] = Field(
        default_factory=lambda: {"morning": 0.5, "afternoon": 0.5, "evening": 0.5, "night": 0.3},
        description="Time preference scores"
    )


class PreferenceScores(BaseModel):
    """Schema for preference scores"""
    categories: Dict[str, float] = Field(default_factory=dict, description="Category preference scores")
    exam_types: Dict[str, float] = Field(default_factory=dict, description="Exam type preference scores")
    locations: Dict[str, float] = Field(default_factory=dict, description="Location preference scores")
    keywords: Dict[str, float] = Field(default_factory=dict, description="Keyword preference scores")
    difficulty_levels: Dict[str, float] = Field(default_factory=dict, description="Difficulty level preference scores")
    sources: Dict[str, float] = Field(default_factory=dict, description="Source preference scores")


class BehavioralPatterns(BaseModel):
    """Schema for behavioral patterns"""
    avg_session_duration: float = Field(0, description="Average session duration in minutes")
    preferred_content_length: str = Field("medium", description="Preferred content length: short, medium, long")
    interaction_frequency: str = Field("medium", description="Interaction frequency: low, medium, high")
    notification_preferences: str = Field("immediate", description="Notification preferences: immediate, daily, weekly")


class UserInteractionHistory(BaseModel):
    """Schema for user interaction history"""
    type: str = Field(..., description="Type of interaction")
    announcement_id: str = Field(..., description="ID of the announcement")
    timestamp: str = Field(..., description="Timestamp of the interaction")
    weight: float = Field(..., description="Weight of the interaction")


class UserProfile(BaseModel):
    """Schema for user profile"""
    preferences: UserPreferences = Field(..., description="User preferences")
    interactions: List[UserInteractionHistory] = Field(default_factory=list, description="User interaction history")
    preference_scores: PreferenceScores = Field(..., description="Calculated preference scores")
    behavioral_patterns: BehavioralPatterns = Field(..., description="User behavioral patterns")
    last_updated: str = Field(..., description="Last update timestamp")


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    success: bool = Field(..., description="Whether the request was successful")
    profile: UserProfile = Field(..., description="User profile data")
    user_id: str = Field(..., description="User ID")


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    categories: Optional[List[str]] = Field(None, description="Updated categories")
    exam_types: Optional[List[str]] = Field(None, description="Updated exam types")
    locations: Optional[List[str]] = Field(None, description="Updated locations")
    keywords: Optional[List[str]] = Field(None, description="Updated keywords")
    difficulty_levels: Optional[List[str]] = Field(None, description="Updated difficulty levels")


class SimilarUser(BaseModel):
    """Schema for similar user"""
    user_id: str = Field(..., description="User ID")
    similarity_score: float = Field(..., description="Similarity score")
    common_preferences: List[str] = Field(..., description="Common preferences")


class PersonalizationInsights(BaseModel):
    """Schema for personalization insights"""
    total_interactions: int = Field(..., description="Total number of interactions")
    preferred_categories: List[tuple] = Field(..., description="Top preferred categories with scores")
    preferred_exam_types: List[tuple] = Field(..., description="Top preferred exam types with scores")
    preferred_locations: List[tuple] = Field(..., description="Top preferred locations with scores")
    preferred_keywords: List[tuple] = Field(..., description="Top preferred keywords with scores")
    behavioral_patterns: BehavioralPatterns = Field(..., description="User behavioral patterns")
    last_updated: str = Field(..., description="Last update timestamp")


class RecommendationExplanation(BaseModel):
    """Schema for recommendation explanation"""
    announcement_id: str = Field(..., description="Announcement ID")
    recommendation_score: float = Field(..., description="Recommendation score")
    reasons: List[str] = Field(..., description="Reasons for recommendation")
    explanation: str = Field(..., description="Human-readable explanation")


class PersonalizationMetrics(BaseModel):
    """Schema for personalization metrics"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    avg_interactions_per_user: float = Field(..., description="Average interactions per user")
    recommendation_accuracy: float = Field(..., description="Recommendation accuracy score")
    user_engagement_score: float = Field(..., description="Overall user engagement score")
    top_categories: List[tuple] = Field(..., description="Top categories across all users")
    top_exam_types: List[tuple] = Field(..., description="Top exam types across all users")


class PersonalizationStatus(BaseModel):
    """Schema for personalization service status"""
    service_active: bool = Field(..., description="Whether the service is active")
    total_profiles: int = Field(..., description="Total number of user profiles")
    last_processing_time: Optional[str] = Field(None, description="Last processing time")
    recommendation_engine_status: str = Field(..., description="Status of recommendation engine")
    learning_algorithm_status: str = Field(..., description="Status of learning algorithm")
    cache_status: Dict[str, Any] = Field(..., description="Cache status information")
