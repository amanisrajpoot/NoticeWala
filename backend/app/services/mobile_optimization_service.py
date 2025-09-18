"""
Mobile Optimization Service

Handles mobile-specific optimizations for offline-first architecture,
including data compression, caching strategies, and performance optimization.
"""

import structlog
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
import json
import gzip
import base64
import hashlib
import uuid

from app.models.user import User
from app.models.announcement import Announcement
from app.models.user import Subscription
from app.core.database import get_db

logger = structlog.get_logger()


class MobileOptimizationService:
    def __init__(self):
        self.compression_threshold = 1024  # bytes
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 50 * 1024 * 1024  # 50MB
        self.image_quality = 80  # percentage
        self.thumbnail_size = (300, 200)  # width, height
        
    async def optimize_for_mobile(
        self, 
        db: Session, 
        user_id: str, 
        data: Dict[str, Any],
        optimization_level: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Optimize data for mobile consumption.
        
        Args:
            user_id: User ID
            data: Raw data to optimize
            optimization_level: Level of optimization (minimal, balanced, aggressive)
            
        Returns:
            Optimized data for mobile
        """
        logger.info("Optimizing data for mobile", 
                   user_id=user_id, 
                   optimization_level=optimization_level)
        
        try:
            optimized_data = {}
            
            # Optimize announcements
            if "announcements" in data:
                optimized_data["announcements"] = await self._optimize_announcements(
                    data["announcements"], 
                    optimization_level
                )
            
            # Optimize user preferences
            if "user_preferences" in data:
                optimized_data["user_preferences"] = self._optimize_preferences(
                    data["user_preferences"]
                )
            
            # Optimize subscriptions
            if "subscriptions" in data:
                optimized_data["subscriptions"] = self._optimize_subscriptions(
                    data["subscriptions"]
                )
            
            # Add mobile-specific metadata
            optimized_data["mobile_metadata"] = {
                "optimization_level": optimization_level,
                "compression_used": self._should_compress(optimized_data),
                "cache_ttl": self.cache_ttl,
                "optimized_at": datetime.utcnow().isoformat()
            }
            
            # Compress if needed
            if self._should_compress(optimized_data):
                optimized_data = self._compress_data(optimized_data)
            
            logger.info("Data optimized for mobile", 
                       user_id=user_id, 
                       original_size=self._get_data_size(data),
                       optimized_size=self._get_data_size(optimized_data))
            
            return optimized_data
            
        except Exception as e:
            logger.error("Failed to optimize data for mobile", 
                        user_id=user_id, 
                        error=str(e))
            raise
    
    async def _optimize_announcements(
        self, 
        announcements: List[Dict[str, Any]], 
        optimization_level: str
    ) -> List[Dict[str, Any]]:
        """Optimize announcement data for mobile."""
        
        optimized = []
        
        for announcement in announcements:
            # Create mobile-optimized version
            mobile_announcement = {
                "id": announcement.get("id"),
                "title": announcement.get("title"),
                "summary": announcement.get("summary", "")[:200],  # Truncate summary
                "categories": announcement.get("categories", []),
                "exam_type": announcement.get("exam_type"),
                "priority_score": announcement.get("priority_score"),
                "created_at": announcement.get("created_at"),
                "application_deadline": announcement.get("application_deadline"),
                "exam_date": announcement.get("exam_date"),
                "is_active": announcement.get("is_active"),
                "tags": announcement.get("tags", [])[:5],  # Limit tags
            }
            
            # Add full data for aggressive optimization
            if optimization_level == "aggressive":
                mobile_announcement["description"] = announcement.get("description", "")[:500]
                mobile_announcement["region"] = announcement.get("region")
                mobile_announcement["location"] = announcement.get("location")
            
            # Add minimal data for minimal optimization
            elif optimization_level == "minimal":
                mobile_announcement["description"] = announcement.get("description")
                mobile_announcement["region"] = announcement.get("region")
                mobile_announcement["location"] = announcement.get("location")
                mobile_announcement["source_id"] = announcement.get("source_id")
                mobile_announcement["ai_processed"] = announcement.get("ai_processed")
            
            optimized.append(mobile_announcement)
        
        return optimized
    
    def _optimize_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize user preferences for mobile."""
        
        # Remove unnecessary fields and compress values
        optimized = {}
        
        for key, value in preferences.items():
            if key in ["categories", "keywords", "regions"]:
                # Limit list sizes
                if isinstance(value, list):
                    optimized[key] = value[:20]
                else:
                    optimized[key] = value
            elif key in ["language", "timezone", "notification_frequency"]:
                optimized[key] = value
            # Skip other fields for mobile optimization
        
        return optimized
    
    def _optimize_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize subscription data for mobile."""
        
        optimized = []
        
        for subscription in subscriptions:
            mobile_subscription = {
                "id": subscription.get("id"),
                "categories": subscription.get("categories", []),
                "regions": subscription.get("regions", []),
                "exam_types": subscription.get("exam_types", []),
                "is_active": subscription.get("is_active"),
                "created_at": subscription.get("created_at")
            }
            
            # Add keywords only if they exist and are not too many
            if subscription.get("keywords"):
                keywords = subscription["keywords"]
                if isinstance(keywords, list) and len(keywords) <= 10:
                    mobile_subscription["keywords"] = keywords
            
            optimized.append(mobile_subscription)
        
        return optimized
    
    def _should_compress(self, data: Dict[str, Any]) -> bool:
        """Determine if data should be compressed."""
        data_size = self._get_data_size(data)
        return data_size > self.compression_threshold
    
    def _get_data_size(self, data: Dict[str, Any]) -> int:
        """Calculate approximate data size in bytes."""
        try:
            json_str = json.dumps(data, default=str)
            return len(json_str.encode('utf-8'))
        except:
            return 0
    
    def _compress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress data using gzip."""
        try:
            json_str = json.dumps(data, default=str)
            compressed = gzip.compress(json_str.encode('utf-8'))
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')
            
            return {
                "compressed": True,
                "data": compressed_b64,
                "original_size": len(json_str),
                "compressed_size": len(compressed)
            }
        except Exception as e:
            logger.error("Failed to compress data", error=str(e))
            return data
    
    def _decompress_data(self, compressed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress gzipped data."""
        try:
            if not compressed_data.get("compressed"):
                return compressed_data
            
            compressed_b64 = compressed_data["data"]
            compressed = base64.b64decode(compressed_b64)
            json_str = gzip.decompress(compressed).decode('utf-8')
            
            return json.loads(json_str)
        except Exception as e:
            logger.error("Failed to decompress data", error=str(e))
            return compressed_data
    
    async def get_mobile_cache_strategy(
        self, 
        db: Session, 
        user_id: str
    ) -> Dict[str, Any]:
        """Get optimal caching strategy for mobile user."""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Analyze user behavior to determine cache strategy
            user_preferences = user.preferences or {}
            
            # Determine cache duration based on user activity
            cache_duration = 3600  # Default 1 hour
            
            if user_preferences.get("notification_frequency") == "realtime":
                cache_duration = 300  # 5 minutes
            elif user_preferences.get("notification_frequency") == "hourly":
                cache_duration = 1800  # 30 minutes
            elif user_preferences.get("notification_frequency") == "daily":
                cache_duration = 86400  # 24 hours
            
            # Determine data priority based on user preferences
            priority_categories = user_preferences.get("categories", [])
            priority_regions = user_preferences.get("regions", [])
            
            cache_strategy = {
                "cache_duration": cache_duration,
                "priority_categories": priority_categories,
                "priority_regions": priority_regions,
                "max_cache_size": self.max_cache_size,
                "compression_enabled": True,
                "preload_critical_data": True,
                "background_refresh": True
            }
            
            return cache_strategy
            
        except Exception as e:
            logger.error("Failed to get mobile cache strategy", 
                        user_id=user_id, 
                        error=str(e))
            return {"error": str(e)}
    
    async def optimize_images_for_mobile(
        self, 
        image_urls: List[str], 
        optimization_level: str = "balanced"
    ) -> List[Dict[str, str]]:
        """Optimize images for mobile consumption."""
        
        optimized_images = []
        
        for url in image_urls:
            # Generate mobile-optimized image URLs
            # This would typically involve image processing service
            mobile_url = f"{url}?w={self.thumbnail_size[0]}&h={self.thumbnail_size[1]}&q={self.image_quality}"
            thumbnail_url = f"{url}?w=150&h=100&q=70"
            
            optimized_images.append({
                "original_url": url,
                "mobile_url": mobile_url,
                "thumbnail_url": thumbnail_url,
                "optimization_level": optimization_level
            })
        
        return optimized_images
    
    async def get_offline_storage_recommendations(
        self, 
        db: Session, 
        user_id: str
    ) -> Dict[str, Any]:
        """Get recommendations for offline storage management."""
        
        try:
            # Get user's data usage patterns
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Calculate estimated storage needs
            user_subscriptions = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).count()
            
            # Estimate based on subscription count and preferences
            estimated_announcements = user_subscriptions * 50  # Rough estimate
            estimated_storage = estimated_announcements * 5 * 1024  # 5KB per announcement
            
            recommendations = {
                "estimated_storage_needed": estimated_storage,
                "recommended_cache_size": min(estimated_storage * 2, self.max_cache_size),
                "cleanup_frequency": "weekly" if estimated_storage > 10 * 1024 * 1024 else "monthly",
                "compression_recommended": estimated_storage > 5 * 1024 * 1024,
                "priority_data": [
                    "high_priority_announcements",
                    "user_preferences",
                    "active_subscriptions"
                ],
                "optional_data": [
                    "historical_announcements",
                    "detailed_descriptions",
                    "full_attachments"
                ]
            }
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to get offline storage recommendations", 
                        user_id=user_id, 
                        error=str(e))
            return {"error": str(e)}


# Global instance
mobile_optimization_service = MobileOptimizationService()
