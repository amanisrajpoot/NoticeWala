"""
Analytics schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserInteractionTrack(BaseModel):
    """Schema for tracking user interactions"""
    interaction_type: str = Field(..., description="Type of interaction: view, click, bookmark, share, download, subscribe, dismiss")
    announcement_id: str = Field(..., description="ID of the announcement interacted with")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the interaction")


class EngagementMetrics(BaseModel):
    """Schema for user engagement metrics"""
    total_interactions: int = Field(..., description="Total number of interactions")
    daily_average: float = Field(..., description="Daily average interactions")
    session_duration_avg: float = Field(..., description="Average session duration in minutes")
    pages_per_session: float = Field(..., description="Average pages per session")
    bounce_rate: float = Field(..., description="Bounce rate percentage")
    return_visitor_rate: float = Field(..., description="Return visitor rate")
    engagement_score: float = Field(..., description="Overall engagement score (0-1)")
    interaction_breakdown: Dict[str, int] = Field(..., description="Breakdown of interaction types")
    time_based_patterns: Dict[str, Any] = Field(..., description="Time-based usage patterns")


class ContentPreferences(BaseModel):
    """Schema for user content preferences"""
    preferred_categories: List[str] = Field(..., description="Preferred exam categories")
    preferred_exam_types: List[str] = Field(..., description="Preferred exam types")
    preferred_locations: List[str] = Field(..., description="Preferred locations")
    preferred_keywords: List[str] = Field(..., description="Preferred keywords")
    content_length_preference: str = Field(..., description="Preferred content length")
    difficulty_preference: str = Field(..., description="Preferred difficulty level")
    source_preferences: List[str] = Field(..., description="Preferred content sources")
    time_preferences: Dict[str, float] = Field(..., description="Time-based preferences")


class BehavioralPatterns(BaseModel):
    """Schema for user behavioral patterns"""
    usage_frequency: str = Field(..., description="Usage frequency: low, medium, high")
    session_patterns: Dict[str, float] = Field(..., description="Session-related patterns")
    navigation_patterns: Dict[str, Any] = Field(..., description="Navigation patterns")
    search_patterns: Dict[str, Any] = Field(..., description="Search behavior patterns")
    notification_patterns: Dict[str, Any] = Field(..., description="Notification interaction patterns")


class SubscriptionAnalytics(BaseModel):
    """Schema for subscription analytics"""
    total_subscriptions: int = Field(..., description="Total number of subscriptions")
    active_subscriptions: int = Field(..., description="Number of active subscriptions")
    subscription_categories: List[str] = Field(..., description="Categories of subscriptions")
    notification_preferences: Dict[str, int] = Field(..., description="Notification preference distribution")
    subscription_effectiveness: Dict[str, float] = Field(..., description="Subscription effectiveness metrics")


class NotificationAnalytics(BaseModel):
    """Schema for notification analytics"""
    total_notifications_sent: int = Field(..., description="Total notifications sent")
    notifications_opened: int = Field(..., description="Number of notifications opened")
    open_rate: float = Field(..., description="Notification open rate")
    click_through_rate: float = Field(..., description="Click-through rate")
    notification_timing_effectiveness: Dict[str, float] = Field(..., description="Effectiveness by time of day")
    notification_types_performance: Dict[str, float] = Field(..., description="Performance by notification type")


class PerformanceInsights(BaseModel):
    """Schema for performance insights"""
    engagement_trend: str = Field(..., description="Engagement trend: increasing, decreasing, stable")
    content_discovery_efficiency: float = Field(..., description="Content discovery efficiency score")
    time_to_find_relevant_content: float = Field(..., description="Average time to find relevant content")
    satisfaction_indicators: Dict[str, float] = Field(..., description="Satisfaction indicators")
    improvement_opportunities: List[str] = Field(..., description="Identified improvement opportunities")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")


class UserAnalytics(BaseModel):
    """Schema for user analytics"""
    user_id: str = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    generated_at: str = Field(..., description="Analysis generation timestamp")
    engagement_metrics: EngagementMetrics = Field(..., description="Engagement metrics")
    content_preferences: ContentPreferences = Field(..., description="Content preferences")
    behavioral_patterns: BehavioralPatterns = Field(..., description="Behavioral patterns")
    subscription_analytics: SubscriptionAnalytics = Field(..., description="Subscription analytics")
    notification_analytics: NotificationAnalytics = Field(..., description="Notification analytics")
    performance_insights: PerformanceInsights = Field(..., description="Performance insights")


class UserAnalyticsResponse(BaseModel):
    """Schema for user analytics response"""
    success: bool = Field(..., description="Whether the request was successful")
    analytics: UserAnalytics = Field(..., description="User analytics data")
    user_id: str = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")


class SystemUserMetrics(BaseModel):
    """Schema for system user metrics"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    user_growth_rate: float = Field(..., description="User growth rate")
    user_retention_rate: float = Field(..., description="User retention rate")
    new_users_today: int = Field(..., description="New users today")
    new_users_this_week: int = Field(..., description="New users this week")
    new_users_this_month: int = Field(..., description="New users this month")
    user_engagement_distribution: Dict[str, int] = Field(..., description="User engagement distribution")


class SystemContentMetrics(BaseModel):
    """Schema for system content metrics"""
    total_announcements: int = Field(..., description="Total number of announcements")
    recent_announcements: int = Field(..., description="Recent announcements count")
    content_growth_rate: float = Field(..., description="Content growth rate")
    content_quality_score: float = Field(..., description="Content quality score")
    top_categories: List[Dict[str, Any]] = Field(..., description="Top categories")
    top_exam_types: List[Dict[str, Any]] = Field(..., description="Top exam types")
    content_performance: Dict[str, float] = Field(..., description="Content performance metrics")


class SystemEngagementMetrics(BaseModel):
    """Schema for system engagement metrics"""
    total_interactions: int = Field(..., description="Total interactions")
    daily_active_users: int = Field(..., description="Daily active users")
    weekly_active_users: int = Field(..., description="Weekly active users")
    monthly_active_users: int = Field(..., description="Monthly active users")
    avg_session_duration: float = Field(..., description="Average session duration")
    bounce_rate: float = Field(..., description="Bounce rate")
    pages_per_session: float = Field(..., description="Pages per session")
    engagement_trends: Dict[str, List[Any]] = Field(..., description="Engagement trends over time")


class SystemPerformanceMetrics(BaseModel):
    """Schema for system performance metrics"""
    api_response_time: float = Field(..., description="API response time in milliseconds")
    search_response_time: float = Field(..., description="Search response time in milliseconds")
    recommendation_generation_time: float = Field(..., description="Recommendation generation time")
    system_uptime: float = Field(..., description="System uptime percentage")
    error_rate: float = Field(..., description="Error rate percentage")
    throughput: float = Field(..., description="Throughput per second")
    cache_hit_rate: float = Field(..., description="Cache hit rate")


class SystemTrends(BaseModel):
    """Schema for system trends"""
    user_growth_trend: str = Field(..., description="User growth trend")
    content_growth_trend: str = Field(..., description="Content growth trend")
    engagement_trend: str = Field(..., description="Engagement trend")
    popular_categories_trend: List[Dict[str, Any]] = Field(..., description="Popular categories trend")
    search_trends: List[Dict[str, Any]] = Field(..., description="Search trends")
    notification_trends: List[Dict[str, Any]] = Field(..., description="Notification trends")


class SystemAnalytics(BaseModel):
    """Schema for system analytics"""
    period_days: int = Field(..., description="Analysis period in days")
    generated_at: str = Field(..., description="Analysis generation timestamp")
    user_metrics: SystemUserMetrics = Field(..., description="User metrics")
    content_metrics: SystemContentMetrics = Field(..., description="Content metrics")
    engagement_metrics: SystemEngagementMetrics = Field(..., description="Engagement metrics")
    performance_metrics: SystemPerformanceMetrics = Field(..., description="Performance metrics")
    trends: SystemTrends = Field(..., description="System trends")
    insights: List[str] = Field(..., description="System insights")


class SystemAnalyticsResponse(BaseModel):
    """Schema for system analytics response"""
    success: bool = Field(..., description="Whether the request was successful")
    analytics: SystemAnalytics = Field(..., description="System analytics data")
    period_days: int = Field(..., description="Analysis period in days")


class ContentAnalytics(BaseModel):
    """Schema for content analytics"""
    content_id: Optional[str] = Field(None, description="Content ID if specific content")
    period_days: int = Field(..., description="Analysis period in days")
    generated_at: str = Field(..., description="Analysis generation timestamp")
    views: int = Field(..., description="Number of views")
    bookmarks: int = Field(..., description="Number of bookmarks")
    shares: int = Field(..., description="Number of shares")
    engagement_rate: float = Field(..., description="Engagement rate")
    popularity_score: float = Field(..., description="Popularity score")
    user_demographics: Dict[str, Any] = Field(..., description="User demographics")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")


class ContentAnalyticsResponse(BaseModel):
    """Schema for content analytics response"""
    success: bool = Field(..., description="Whether the request was successful")
    analytics: ContentAnalytics = Field(..., description="Content analytics data")
    content_id: Optional[str] = Field(None, description="Content ID if specific content")
    period_days: int = Field(..., description="Analysis period in days")


class RecommendationMetrics(BaseModel):
    """Schema for recommendation metrics"""
    total_recommendations_generated: int = Field(..., description="Total recommendations generated")
    recommendation_accuracy: float = Field(..., description="Recommendation accuracy")
    user_satisfaction_score: float = Field(..., description="User satisfaction score")
    click_through_rate: float = Field(..., description="Click-through rate")
    conversion_rate: float = Field(..., description="Conversion rate")
    algorithm_performance: Dict[str, float] = Field(..., description="Algorithm performance metrics")


class CTRMetrics(BaseModel):
    """Schema for click-through rate metrics"""
    overall_ctr: float = Field(..., description="Overall click-through rate")
    ctr_by_recommendation_type: Dict[str, float] = Field(..., description="CTR by recommendation type")
    ctr_by_category: Dict[str, float] = Field(..., description="CTR by category")
    ctr_trends: List[Dict[str, Any]] = Field(..., description="CTR trends over time")


class ConversionMetrics(BaseModel):
    """Schema for conversion metrics"""
    overall_conversion_rate: float = Field(..., description="Overall conversion rate")
    conversion_by_source: Dict[str, float] = Field(..., description="Conversion by source")
    conversion_by_category: Dict[str, float] = Field(..., description="Conversion by category")
    conversion_funnel: Dict[str, int] = Field(..., description="Conversion funnel metrics")


class SatisfactionMetrics(BaseModel):
    """Schema for satisfaction metrics"""
    overall_satisfaction: float = Field(..., description="Overall satisfaction score")
    satisfaction_by_feature: Dict[str, float] = Field(..., description="Satisfaction by feature")
    satisfaction_trends: List[Dict[str, Any]] = Field(..., description="Satisfaction trends")
    user_feedback_summary: List[str] = Field(..., description="User feedback summary")


class AlgorithmPerformance(BaseModel):
    """Schema for algorithm performance"""
    recommendation_accuracy: float = Field(..., description="Recommendation accuracy")
    diversity_score: float = Field(..., description="Diversity score")
    novelty_score: float = Field(..., description="Novelty score")
    coverage_score: float = Field(..., description="Coverage score")
    algorithm_comparison: Dict[str, float] = Field(..., description="Algorithm comparison metrics")


class RecommendationAnalytics(BaseModel):
    """Schema for recommendation analytics"""
    period_days: int = Field(..., description="Analysis period in days")
    generated_at: str = Field(..., description="Analysis generation timestamp")
    user_specific: bool = Field(..., description="Whether analytics are user-specific")
    recommendation_metrics: RecommendationMetrics = Field(..., description="Recommendation metrics")
    click_through_rates: CTRMetrics = Field(..., description="Click-through rate metrics")
    conversion_rates: ConversionMetrics = Field(..., description="Conversion metrics")
    user_satisfaction: SatisfactionMetrics = Field(..., description="Satisfaction metrics")
    algorithm_performance: AlgorithmPerformance = Field(..., description="Algorithm performance")


class RecommendationAnalyticsResponse(BaseModel):
    """Schema for recommendation analytics response"""
    success: bool = Field(..., description="Whether the request was successful")
    analytics: RecommendationAnalytics = Field(..., description="Recommendation analytics data")
    user_id: Optional[str] = Field(None, description="User ID if user-specific")
    period_days: int = Field(..., description="Analysis period in days")


class AnalyticsInsight(BaseModel):
    """Schema for analytics insights"""
    type: str = Field(..., description="Insight type: positive, negative, improvement, info")
    category: str = Field(..., description="Insight category")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    recommendation: str = Field(..., description="Recommendation based on insight")
    priority: str = Field("medium", description="Insight priority: low, medium, high")
    confidence: float = Field(..., description="Confidence score (0-1)")


class AnalyticsDashboard(BaseModel):
    """Schema for analytics dashboard"""
    user_analytics: UserAnalytics = Field(..., description="User analytics")
    system_analytics: SystemAnalytics = Field(..., description="System analytics")
    recommendation_analytics: RecommendationAnalytics = Field(..., description="Recommendation analytics")
    summary: Dict[str, Any] = Field(..., description="Dashboard summary")


class AnalyticsExport(BaseModel):
    """Schema for analytics export"""
    format: str = Field(..., description="Export format: json, csv, xlsx")
    data_type: str = Field(..., description="Data type: user, system, content")
    period_days: int = Field(..., description="Analysis period in days")
    exported_at: str = Field(..., description="Export timestamp")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL for the export")
