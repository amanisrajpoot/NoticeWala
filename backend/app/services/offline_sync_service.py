"""
Offline-First Mobile Architecture Service

This service handles offline data synchronization, conflict resolution,
and ensures seamless user experience across online/offline states.
"""

import structlog
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
import json
import hashlib
import uuid

from app.models.user import User
from app.models.announcement import Announcement
from app.models.user import Subscription
from app.core.database import get_db

logger = structlog.get_logger()


class OfflineSyncService:
    def __init__(self):
        self.sync_conflict_resolution = "server_wins"  # or "client_wins", "merge"
        self.max_sync_batch_size = 100
        self.sync_timeout = 30  # seconds
        
    async def get_sync_data(
        self, 
        db: Session, 
        user_id: str, 
        last_sync_timestamp: Optional[datetime] = None,
        sync_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Get data for offline synchronization based on user's last sync time.
        
        Args:
            user_id: User ID requesting sync
            last_sync_timestamp: Last successful sync timestamp
            sync_type: Type of sync (full, incremental, delta)
            
        Returns:
            Dictionary containing sync data and metadata
        """
        logger.info("Starting offline sync", user_id=user_id, sync_type=sync_type)
        
        try:
            # Get user's subscriptions and preferences
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Base query for announcements
            query = db.query(Announcement).filter(Announcement.is_active == True)
            
            # Apply incremental sync filter
            if last_sync_timestamp and sync_type == "incremental":
                query = query.filter(
                    or_(
                        Announcement.created_at > last_sync_timestamp,
                        Announcement.updated_at > last_sync_timestamp
                    )
                )
            
            # Apply user's subscription filters
            user_subscriptions = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).all()
            
            if user_subscriptions:
                subscription_filters = []
                for sub in user_subscriptions:
                    if sub.categories:
                        subscription_filters.append(
                            Announcement.categories.overlap(sub.categories)
                        )
                    if sub.regions:
                        subscription_filters.append(
                            Announcement.region.in_(sub.regions)
                        )
                    if sub.exam_types:
                        subscription_filters.append(
                            Announcement.exam_type.in_(sub.exam_types)
                        )
                
                if subscription_filters:
                    query = query.filter(or_(*subscription_filters))
            
            # Get announcements with pagination
            announcements = query.order_by(desc(Announcement.created_at)).limit(
                self.max_sync_batch_size
            ).all()
            
            # Prepare sync data
            sync_data = {
                "sync_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "sync_type": sync_type,
                "user_id": user_id,
                "data": {
                    "announcements": [self._serialize_announcement(ann) for ann in announcements],
                    "user_preferences": user.preferences or {},
                    "subscriptions": [self._serialize_subscription(sub) for sub in user_subscriptions]
                },
                "metadata": {
                    "total_announcements": len(announcements),
                    "has_more": len(announcements) == self.max_sync_batch_size,
                    "sync_version": "1.0"
                }
            }
            
            logger.info("Offline sync data prepared", 
                       user_id=user_id, 
                       announcement_count=len(announcements))
            
            return sync_data
            
        except Exception as e:
            logger.error("Failed to get sync data", user_id=user_id, error=str(e))
            raise
    
    async def process_offline_changes(
        self, 
        db: Session, 
        user_id: str, 
        offline_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process changes made while offline and resolve conflicts.
        
        Args:
            user_id: User ID submitting changes
            offline_changes: List of changes made offline
            
        Returns:
            Dictionary containing sync results and conflicts
        """
        logger.info("Processing offline changes", 
                   user_id=user_id, 
                   change_count=len(offline_changes))
        
        try:
            sync_results = {
                "processed": 0,
                "conflicts": [],
                "errors": [],
                "successful": []
            }
            
            for change in offline_changes:
                try:
                    result = await self._process_single_change(db, user_id, change)
                    if result["status"] == "success":
                        sync_results["successful"].append(result)
                    elif result["status"] == "conflict":
                        sync_results["conflicts"].append(result)
                    else:
                        sync_results["errors"].append(result)
                    
                    sync_results["processed"] += 1
                    
                except Exception as e:
                    logger.error("Failed to process offline change", 
                               user_id=user_id, 
                               change=change, 
                               error=str(e))
                    sync_results["errors"].append({
                        "change_id": change.get("id"),
                        "error": str(e),
                        "status": "error"
                    })
            
            logger.info("Offline changes processed", 
                       user_id=user_id, 
                       results=sync_results)
            
            return sync_results
            
        except Exception as e:
            logger.error("Failed to process offline changes", 
                        user_id=user_id, 
                        error=str(e))
            raise
    
    async def _process_single_change(
        self, 
        db: Session, 
        user_id: str, 
        change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single offline change and handle conflicts."""
        
        change_type = change.get("type")
        change_id = change.get("id")
        
        if change_type == "user_interaction":
            return await self._process_user_interaction(db, user_id, change)
        elif change_type == "preference_update":
            return await self._process_preference_update(db, user_id, change)
        elif change_type == "subscription_update":
            return await self._process_subscription_update(db, user_id, change)
        else:
            return {
                "change_id": change_id,
                "status": "error",
                "error": f"Unknown change type: {change_type}"
            }
    
    async def _process_user_interaction(
        self, 
        db: Session, 
        user_id: str, 
        change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user interaction changes (views, bookmarks, etc.)."""
        
        try:
            # Record user interaction for analytics
            # This would typically update user activity logs
            logger.info("Processing user interaction", 
                       user_id=user_id, 
                       interaction=change.get("interaction_type"))
            
            return {
                "change_id": change.get("id"),
                "status": "success",
                "message": "User interaction recorded"
            }
            
        except Exception as e:
            return {
                "change_id": change.get("id"),
                "status": "error",
                "error": str(e)
            }
    
    async def _process_preference_update(
        self, 
        db: Session, 
        user_id: str, 
        change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user preference updates."""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "change_id": change.get("id"),
                    "status": "error",
                    "error": "User not found"
                }
            
            # Merge preferences with conflict resolution
            current_preferences = user.preferences or {}
            new_preferences = change.get("preferences", {})
            
            # Simple merge strategy (can be enhanced)
            merged_preferences = {**current_preferences, **new_preferences}
            
            user.preferences = merged_preferences
            db.commit()
            
            return {
                "change_id": change.get("id"),
                "status": "success",
                "message": "Preferences updated"
            }
            
        except Exception as e:
            return {
                "change_id": change.get("id"),
                "status": "error",
                "error": str(e)
            }
    
    async def _process_subscription_update(
        self, 
        db: Session, 
        user_id: str, 
        change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process subscription updates."""
        
        try:
            subscription_data = change.get("subscription", {})
            subscription_id = subscription_data.get("id")
            
            if subscription_id:
                # Update existing subscription
                subscription = db.query(Subscription).filter(
                    Subscription.id == subscription_id,
                    Subscription.user_id == user_id
                ).first()
                
                if subscription:
                    # Update subscription fields
                    for key, value in subscription_data.items():
                        if hasattr(subscription, key) and key != "id":
                            setattr(subscription, key, value)
                    
                    db.commit()
                    
                    return {
                        "change_id": change.get("id"),
                        "status": "success",
                        "message": "Subscription updated"
                    }
                else:
                    return {
                        "change_id": change.get("id"),
                        "status": "error",
                        "error": "Subscription not found"
                    }
            else:
                # Create new subscription
                new_subscription = Subscription(
                    user_id=user_id,
                    **subscription_data
                )
                db.add(new_subscription)
                db.commit()
                
                return {
                    "change_id": change.get("id"),
                    "status": "success",
                    "message": "Subscription created"
                }
                
        except Exception as e:
            return {
                "change_id": change.get("id"),
                "status": "error",
                "error": str(e)
            }
    
    def _serialize_announcement(self, announcement: Announcement) -> Dict[str, Any]:
        """Serialize announcement for offline storage."""
        return {
            "id": str(announcement.id),
            "title": announcement.title,
            "description": announcement.description,
            "summary": announcement.summary,
            "categories": announcement.categories,
            "exam_type": announcement.exam_type,
            "region": announcement.region,
            "priority_score": announcement.priority_score,
            "created_at": announcement.created_at.isoformat() if announcement.created_at else None,
            "updated_at": announcement.updated_at.isoformat() if announcement.updated_at else None,
            "application_deadline": announcement.application_deadline.isoformat() if announcement.application_deadline else None,
            "exam_date": announcement.exam_date.isoformat() if announcement.exam_date else None,
            "is_active": announcement.is_active,
            "source_id": str(announcement.source_id) if announcement.source_id else None,
            "tags": announcement.tags,
            "location": announcement.location,
            "ai_processed": announcement.ai_processed,
            "ai_data": announcement.ai_data
        }
    
    def _serialize_subscription(self, subscription: Subscription) -> Dict[str, Any]:
        """Serialize subscription for offline storage."""
        return {
            "id": str(subscription.id),
            "user_id": str(subscription.user_id),
            "categories": subscription.categories,
            "regions": subscription.regions,
            "exam_types": subscription.exam_types,
            "keywords": subscription.keywords,
            "is_active": subscription.is_active,
            "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
            "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None
        }
    
    async def get_sync_status(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get current sync status for a user."""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Get last sync timestamp from user preferences or separate sync log
            last_sync = user.preferences.get("last_sync") if user.preferences else None
            
            # Get pending changes count
            pending_changes = 0  # This would be calculated from offline change logs
            
            return {
                "user_id": user_id,
                "last_sync": last_sync,
                "pending_changes": pending_changes,
                "sync_status": "ready",
                "server_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get sync status", user_id=user_id, error=str(e))
            return {"error": str(e)}


# Global instance
offline_sync_service = OfflineSyncService()
