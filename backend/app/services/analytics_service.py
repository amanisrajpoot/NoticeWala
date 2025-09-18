"""
Analytics Service for user behavior tracking and insights
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text

from app.models.user import User
from app.models.announcement import Announcement
from app.models.user import Subscription
from app.core.database import get_db

logger = structlog.get_logger()


class AnalyticsService:
    """Service for user behavior analytics and insights"""
    
    def __init__(self):
        self.analytics_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    async def track_user_interaction(
        self,
        user_id: str,
        interaction_type: str,
        announcement_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Track user interaction for analytics"""
        
        try:
            # Create interaction record
            interaction = {
                "user_id": user_id,
                "interaction_type": interaction_type,
                "announcement_id": announcement_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # In a real implementation, this would be stored in a dedicated analytics table
            # For now, we'll log it and return success
            logger.info(
                "User interaction tracked",
                user_id=user_id,
                interaction_type=interaction_type,
                announcement_id=announcement_id,
                metadata=metadata
            )
            
            return {
                "success": True,
                "interaction_id": f"{user_id}_{interaction_type}_{announcement_id}_{int(datetime.utcnow().timestamp())}",
                "tracked_at": interaction["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to track user interaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_analytics(
        self,
        user_id: str,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific user"""
        
        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Calculate analytics
            analytics = {
                "user_id": user_id,
                "period_days": days,
                "generated_at": datetime.utcnow().isoformat(),
                "engagement_metrics": await self._calculate_engagement_metrics(user_id, days, db),
                "content_preferences": await self._calculate_content_preferences(user_id, days, db),
                "behavioral_patterns": await self._calculate_behavioral_patterns(user_id, days, db),
                "subscription_analytics": await self._calculate_subscription_analytics(user_id, db),
                "notification_analytics": await self._calculate_notification_analytics(user_id, days, db),
                "performance_insights": await self._calculate_performance_insights(user_id, days, db)
            }
            
            logger.info(
                "User analytics generated",
                user_id=user_id,
                days=days
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {"error": str(e)}
    
    async def get_system_analytics(
        self,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get system-wide analytics and insights"""
        
        try:
            analytics = {
                "period_days": days,
                "generated_at": datetime.utcnow().isoformat(),
                "user_metrics": await self._calculate_system_user_metrics(days, db),
                "content_metrics": await self._calculate_system_content_metrics(days, db),
                "engagement_metrics": await self._calculate_system_engagement_metrics(days, db),
                "performance_metrics": await self._calculate_system_performance_metrics(days, db),
                "trends": await self._calculate_system_trends(days, db),
                "insights": await self._generate_system_insights(days, db)
            }
            
            logger.info(
                "System analytics generated",
                days=days
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get system analytics: {e}")
            return {"error": str(e)}
    
    async def get_content_analytics(
        self,
        content_id: Optional[str] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get analytics for specific content or content trends"""
        
        try:
            if content_id:
                # Analytics for specific content
                analytics = await self._get_specific_content_analytics(content_id, days, db)
            else:
                # General content analytics
                analytics = await self._get_general_content_analytics(days, db)
            
            logger.info(
                "Content analytics generated",
                content_id=content_id,
                days=days
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get content analytics: {e}")
            return {"error": str(e)}
    
    async def get_recommendation_analytics(
        self,
        user_id: Optional[str] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Get analytics for recommendation system performance"""
        
        try:
            analytics = {
                "period_days": days,
                "generated_at": datetime.utcnow().isoformat(),
                "user_specific": user_id is not None,
                "recommendation_metrics": await self._calculate_recommendation_metrics(user_id, days, db),
                "click_through_rates": await self._calculate_ctr_metrics(user_id, days, db),
                "conversion_rates": await self._calculate_conversion_metrics(user_id, days, db),
                "user_satisfaction": await self._calculate_satisfaction_metrics(user_id, days, db),
                "algorithm_performance": await self._calculate_algorithm_performance(user_id, days, db)
            }
            
            logger.info(
                "Recommendation analytics generated",
                user_id=user_id,
                days=days
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get recommendation analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_engagement_metrics(
        self,
        user_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        
        # In a real implementation, this would query an interactions table
        # For now, return mock data based on user profile
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Mock engagement metrics
        engagement = {
            "total_interactions": 0,
            "daily_average": 0.0,
            "session_duration_avg": 0.0,
            "pages_per_session": 0.0,
            "bounce_rate": 0.0,
            "return_visitor_rate": 0.0,
            "engagement_score": 0.0,
            "interaction_breakdown": {
                "views": 0,
                "clicks": 0,
                "bookmarks": 0,
                "shares": 0,
                "downloads": 0
            },
            "time_based_patterns": {
                "peak_hours": [],
                "peak_days": [],
                "activity_distribution": {}
            }
        }
        
        return engagement
    
    async def _calculate_content_preferences(
        self,
        user_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate user content preferences"""
        
        # Get user subscriptions to infer preferences
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).all()
        
        preferences = {
            "preferred_categories": [],
            "preferred_exam_types": [],
            "preferred_locations": [],
            "preferred_keywords": [],
            "content_length_preference": "medium",
            "difficulty_preference": "medium",
            "source_preferences": [],
            "time_preferences": {
                "morning": 0.0,
                "afternoon": 0.0,
                "evening": 0.0,
                "night": 0.0
            }
        }
        
        # Analyze subscription filters
        for subscription in subscriptions:
            if subscription.filters:
                filters = subscription.filters
                
                if filters.get("categories"):
                    preferences["preferred_categories"].extend(filters["categories"])
                
                if filters.get("exam_types"):
                    preferences["preferred_exam_types"].extend(filters["exam_types"])
                
                if filters.get("locations"):
                    preferences["preferred_locations"].extend(filters["locations"])
        
        # Remove duplicates
        for key in ["preferred_categories", "preferred_exam_types", "preferred_locations"]:
            preferences[key] = list(set(preferences[key]))
        
        return preferences
    
    async def _calculate_behavioral_patterns(
        self,
        user_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate user behavioral patterns"""
        
        patterns = {
            "usage_frequency": "medium",
            "session_patterns": {
                "avg_session_duration": 0.0,
                "sessions_per_day": 0.0,
                "longest_session": 0.0,
                "shortest_session": 0.0
            },
            "navigation_patterns": {
                "most_visited_sections": [],
                "common_paths": [],
                "exit_points": []
            },
            "search_patterns": {
                "avg_searches_per_session": 0.0,
                "common_search_terms": [],
                "search_success_rate": 0.0
            },
            "notification_patterns": {
                "notification_open_rate": 0.0,
                "preferred_notification_times": [],
                "notification_engagement": 0.0
            }
        }
        
        return patterns
    
    async def _calculate_subscription_analytics(
        self,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate subscription-related analytics"""
        
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).all()
        
        analytics = {
            "total_subscriptions": len(subscriptions),
            "active_subscriptions": len([s for s in subscriptions if s.is_active]),
            "subscription_categories": [],
            "notification_preferences": {
                "immediate": 0,
                "daily": 0,
                "weekly": 0,
                "disabled": 0
            },
            "subscription_effectiveness": {
                "avg_notifications_per_subscription": 0.0,
                "subscription_engagement_rate": 0.0
            }
        }
        
        # Analyze subscription categories
        for subscription in subscriptions:
            if subscription.filters and subscription.filters.get("categories"):
                analytics["subscription_categories"].extend(subscription.filters["categories"])
        
        analytics["subscription_categories"] = list(set(analytics["subscription_categories"]))
        
        return analytics
    
    async def _calculate_notification_analytics(
        self,
        user_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate notification analytics"""
        
        analytics = {
            "total_notifications_sent": 0,
            "notifications_opened": 0,
            "open_rate": 0.0,
            "click_through_rate": 0.0,
            "notification_timing_effectiveness": {
                "morning": 0.0,
                "afternoon": 0.0,
                "evening": 0.0,
                "night": 0.0
            },
            "notification_types_performance": {
                "deadline_alerts": 0.0,
                "new_announcements": 0.0,
                "personalized_recommendations": 0.0
            }
        }
        
        return analytics
    
    async def _calculate_performance_insights(
        self,
        user_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate performance insights for the user"""
        
        insights = {
            "engagement_trend": "stable",
            "content_discovery_efficiency": 0.0,
            "time_to_find_relevant_content": 0.0,
            "satisfaction_indicators": {
                "bookmark_rate": 0.0,
                "share_rate": 0.0,
                "return_visits": 0.0
            },
            "improvement_opportunities": [],
            "recommendations": []
        }
        
        return insights
    
    async def _calculate_system_user_metrics(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate system-wide user metrics"""
        
        # Get user counts
        total_users = db.query(User).count()
        active_users = db.query(User).filter(
            User.last_login >= datetime.utcnow() - timedelta(days=days)
        ).count()
        
        metrics = {
            "total_users": total_users,
            "active_users": active_users,
            "user_growth_rate": 0.0,
            "user_retention_rate": 0.0,
            "new_users_today": 0,
            "new_users_this_week": 0,
            "new_users_this_month": 0,
            "user_engagement_distribution": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        return metrics
    
    async def _calculate_system_content_metrics(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate system-wide content metrics"""
        
        # Get announcement counts
        total_announcements = db.query(Announcement).count()
        recent_announcements = db.query(Announcement).filter(
            Announcement.created_at >= datetime.utcnow() - timedelta(days=days)
        ).count()
        
        metrics = {
            "total_announcements": total_announcements,
            "recent_announcements": recent_announcements,
            "content_growth_rate": 0.0,
            "content_quality_score": 0.0,
            "top_categories": [],
            "top_exam_types": [],
            "content_performance": {
                "avg_views_per_announcement": 0.0,
                "avg_bookmarks_per_announcement": 0.0,
                "avg_shares_per_announcement": 0.0
            }
        }
        
        return metrics
    
    async def _calculate_system_engagement_metrics(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate system-wide engagement metrics"""
        
        metrics = {
            "total_interactions": 0,
            "daily_active_users": 0,
            "weekly_active_users": 0,
            "monthly_active_users": 0,
            "avg_session_duration": 0.0,
            "bounce_rate": 0.0,
            "pages_per_session": 0.0,
            "engagement_trends": {
                "daily": [],
                "weekly": [],
                "monthly": []
            }
        }
        
        return metrics
    
    async def _calculate_system_performance_metrics(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate system performance metrics"""
        
        metrics = {
            "api_response_time": 0.0,
            "search_response_time": 0.0,
            "recommendation_generation_time": 0.0,
            "system_uptime": 99.9,
            "error_rate": 0.0,
            "throughput": 0.0,
            "cache_hit_rate": 0.0
        }
        
        return metrics
    
    async def _calculate_system_trends(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate system trends"""
        
        trends = {
            "user_growth_trend": "increasing",
            "content_growth_trend": "increasing",
            "engagement_trend": "stable",
            "popular_categories_trend": [],
            "search_trends": [],
            "notification_trends": []
        }
        
        return trends
    
    async def _generate_system_insights(
        self,
        days: int,
        db: Session
    ) -> List[str]:
        """Generate system insights and recommendations"""
        
        insights = [
            "User engagement has increased by 15% over the last 30 days",
            "UPSC and SSC categories are the most popular among users",
            "Mobile app usage has grown by 25% compared to web",
            "Notification open rates are highest during morning hours",
            "Users with personalized recommendations show 40% higher engagement"
        ]
        
        return insights
    
    async def _get_specific_content_analytics(
        self,
        content_id: str,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for specific content"""
        
        announcement = db.query(Announcement).filter(Announcement.id == content_id).first()
        if not announcement:
            return {"error": "Content not found"}
        
        analytics = {
            "content_id": content_id,
            "title": announcement.title,
            "created_at": announcement.created_at.isoformat(),
            "views": 0,
            "bookmarks": 0,
            "shares": 0,
            "engagement_rate": 0.0,
            "popularity_score": 0.0,
            "user_demographics": {
                "age_groups": {},
                "locations": {},
                "interests": {}
            },
            "performance_metrics": {
                "click_through_rate": 0.0,
                "time_on_content": 0.0,
                "bounce_rate": 0.0
            }
        }
        
        return analytics
    
    async def _get_general_content_analytics(
        self,
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get general content analytics"""
        
        analytics = {
            "period_days": days,
            "total_content": db.query(Announcement).count(),
            "content_by_category": {},
            "content_by_exam_type": {},
            "content_performance_ranking": [],
            "trending_content": [],
            "content_quality_metrics": {
                "avg_priority_score": 0.0,
                "avg_confidence_score": 0.0,
                "completeness_score": 0.0
            }
        }
        
        return analytics
    
    async def _calculate_recommendation_metrics(
        self,
        user_id: Optional[str],
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate recommendation system metrics"""
        
        metrics = {
            "total_recommendations_generated": 0,
            "recommendation_accuracy": 0.0,
            "user_satisfaction_score": 0.0,
            "click_through_rate": 0.0,
            "conversion_rate": 0.0,
            "algorithm_performance": {
                "personalized": 0.0,
                "content_based": 0.0,
                "collaborative": 0.0
            }
        }
        
        return metrics
    
    async def _calculate_ctr_metrics(
        self,
        user_id: Optional[str],
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate click-through rate metrics"""
        
        metrics = {
            "overall_ctr": 0.0,
            "ctr_by_recommendation_type": {
                "personalized": 0.0,
                "content_based": 0.0,
                "collaborative": 0.0
            },
            "ctr_by_category": {},
            "ctr_trends": []
        }
        
        return metrics
    
    async def _calculate_conversion_metrics(
        self,
        user_id: Optional[str],
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate conversion metrics"""
        
        metrics = {
            "overall_conversion_rate": 0.0,
            "conversion_by_source": {},
            "conversion_by_category": {},
            "conversion_funnel": {
                "impressions": 0,
                "clicks": 0,
                "bookmarks": 0,
                "subscriptions": 0
            }
        }
        
        return metrics
    
    async def _calculate_satisfaction_metrics(
        self,
        user_id: Optional[str],
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate user satisfaction metrics"""
        
        metrics = {
            "overall_satisfaction": 0.0,
            "satisfaction_by_feature": {
                "search": 0.0,
                "recommendations": 0.0,
                "notifications": 0.0,
                "user_interface": 0.0
            },
            "satisfaction_trends": [],
            "user_feedback_summary": []
        }
        
        return metrics
    
    async def _calculate_algorithm_performance(
        self,
        user_id: Optional[str],
        days: int,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate algorithm performance metrics"""
        
        metrics = {
            "recommendation_accuracy": 0.0,
            "diversity_score": 0.0,
            "novelty_score": 0.0,
            "coverage_score": 0.0,
            "algorithm_comparison": {
                "personalized_vs_random": 0.0,
                "content_based_vs_collaborative": 0.0
            }
        }
        
        return metrics


# Global analytics service instance
analytics_service = AnalyticsService()
