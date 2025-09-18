"""
Background Synchronization Service

Handles background synchronization, push notifications, and automatic
data updates for offline-first mobile architecture.
"""

import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
import asyncio
import json

from app.models.user import User
from app.models.announcement import Announcement
from app.models.user import Subscription
from app.core.database import get_db
from app.services.notification_service import notification_service

logger = structlog.get_logger()


class BackgroundSyncService:
    def __init__(self):
        self.sync_interval = 300  # 5 minutes
        self.batch_size = 100
        self.max_retries = 3
        self.retry_delay = 60  # seconds
        
    async def start_background_sync(self, db: Session):
        """Start background synchronization process."""
        logger.info("Starting background sync service")
        
        try:
            while True:
                await self._sync_all_users(db)
                await asyncio.sleep(self.sync_interval)
                
        except Exception as e:
            logger.error("Background sync service failed", error=str(e))
            # Restart after delay
            await asyncio.sleep(self.retry_delay)
            await self.start_background_sync(db)
    
    async def _sync_all_users(self, db: Session):
        """Sync all active users in background."""
        try:
            # Get users who need sync
            users = db.query(User).filter(
                User.is_active == True,
                User.last_login >= datetime.utcnow() - timedelta(days=7)  # Active in last 7 days
            ).all()
            
            logger.info("Background sync for users", user_count=len(users))
            
            # Process users in batches
            for i in range(0, len(users), self.batch_size):
                batch = users[i:i + self.batch_size]
                await self._sync_user_batch(db, batch)
                
        except Exception as e:
            logger.error("Failed to sync all users", error=str(e))
    
    async def _sync_user_batch(self, db: Session, users: List[User]):
        """Sync a batch of users."""
        tasks = []
        
        for user in users:
            task = self._sync_single_user(db, user)
            tasks.append(task)
        
        # Run tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _sync_single_user(self, db: Session, user: User):
        """Sync data for a single user."""
        try:
            user_id = str(user.id)
            
            # Check if user needs sync
            last_sync = user.preferences.get("last_sync") if user.preferences else None
            if last_sync:
                last_sync_time = datetime.fromisoformat(last_sync)
                if datetime.utcnow() - last_sync_time < timedelta(minutes=5):
                    return  # Skip if synced recently
            
            # Get user's subscriptions
            subscriptions = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).all()
            
            if not subscriptions:
                return  # No active subscriptions
            
            # Get new announcements for user
            new_announcements = await self._get_new_announcements_for_user(
                db, user_id, subscriptions, last_sync
            )
            
            if new_announcements:
                # Send push notification
                await self._send_sync_notification(user, new_announcements)
                
                # Update last sync time
                if not user.preferences:
                    user.preferences = {}
                user.preferences["last_sync"] = datetime.utcnow().isoformat()
                db.commit()
                
                logger.info("User synced successfully", 
                           user_id=user_id, 
                           new_announcements=len(new_announcements))
            
        except Exception as e:
            logger.error("Failed to sync user", 
                        user_id=str(user.id), 
                        error=str(e))
    
    async def _get_new_announcements_for_user(
        self, 
        db: Session, 
        user_id: str, 
        subscriptions: List[Subscription],
        last_sync: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get new announcements for user based on subscriptions."""
        
        try:
            # Build query based on subscriptions
            query = db.query(Announcement).filter(Announcement.is_active == True)
            
            # Apply subscription filters
            subscription_filters = []
            for sub in subscriptions:
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
            
            # Apply time filter for incremental sync
            if last_sync:
                last_sync_time = datetime.fromisoformat(last_sync)
                query = query.filter(
                    or_(
                        Announcement.created_at > last_sync_time,
                        Announcement.updated_at > last_sync_time
                    )
                )
            else:
                # For first sync, get recent announcements only
                query = query.filter(
                    Announcement.created_at >= datetime.utcnow() - timedelta(days=1)
                )
            
            # Get announcements
            announcements = query.order_by(desc(Announcement.created_at)).limit(50).all()
            
            # Convert to dict format
            return [self._serialize_announcement(ann) for ann in announcements]
            
        except Exception as e:
            logger.error("Failed to get new announcements", 
                        user_id=user_id, 
                        error=str(e))
            return []
    
    async def _send_sync_notification(
        self, 
        user: User, 
        announcements: List[Dict[str, Any]]
    ):
        """Send push notification about new announcements."""
        
        try:
            if not announcements:
                return
            
            # Prepare notification data
            notification_data = {
                "title": f"New {len(announcements)} announcement(s) available",
                "body": f"Check out the latest updates in your subscribed categories",
                "data": {
                    "type": "new_announcements",
                    "count": len(announcements),
                    "announcement_ids": [ann["id"] for ann in announcements[:5]]  # First 5 IDs
                }
            }
            
            # Send notification
            await notification_service.send_push_notification(
                user_id=str(user.id),
                title=notification_data["title"],
                body=notification_data["body"],
                data=notification_data["data"]
            )
            
            logger.info("Sync notification sent", 
                       user_id=str(user.id), 
                       announcement_count=len(announcements))
            
        except Exception as e:
            logger.error("Failed to send sync notification", 
                        user_id=str(user.id), 
                        error=str(e))
    
    def _serialize_announcement(self, announcement: Announcement) -> Dict[str, Any]:
        """Serialize announcement for notification."""
        return {
            "id": str(announcement.id),
            "title": announcement.title,
            "summary": announcement.summary,
            "categories": announcement.categories,
            "exam_type": announcement.exam_type,
            "priority_score": announcement.priority_score,
            "created_at": announcement.created_at.isoformat() if announcement.created_at else None
        }
    
    async def force_sync_user(
        self, 
        db: Session, 
        user_id: str
    ) -> Dict[str, Any]:
        """Force immediate sync for a specific user."""
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Get user's subscriptions
            subscriptions = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).all()
            
            # Get all recent announcements
            new_announcements = await self._get_new_announcements_for_user(
                db, user_id, subscriptions, None
            )
            
            # Update last sync time
            if not user.preferences:
                user.preferences = {}
            user.preferences["last_sync"] = datetime.utcnow().isoformat()
            db.commit()
            
            return {
                "success": True,
                "user_id": user_id,
                "new_announcements": len(new_announcements),
                "synced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to force sync user", 
                        user_id=user_id, 
                        error=str(e))
            return {"error": str(e)}
    
    async def get_sync_statistics(self, db: Session) -> Dict[str, Any]:
        """Get background sync statistics."""
        
        try:
            # Get total users
            total_users = db.query(User).filter(User.is_active == True).count()
            
            # Get users synced in last hour
            recent_sync_time = datetime.utcnow() - timedelta(hours=1)
            users_synced_recently = db.query(User).filter(
                User.is_active == True,
                User.preferences["last_sync"].astext >= recent_sync_time.isoformat()
            ).count()
            
            # Get total announcements
            total_announcements = db.query(Announcement).filter(
                Announcement.is_active == True
            ).count()
            
            # Get new announcements today
            today = datetime.utcnow().date()
            new_today = db.query(Announcement).filter(
                Announcement.is_active == True,
                func.date(Announcement.created_at) == today
            ).count()
            
            return {
                "total_users": total_users,
                "users_synced_recently": users_synced_recently,
                "total_announcements": total_announcements,
                "new_announcements_today": new_today,
                "sync_interval": self.sync_interval,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get sync statistics", error=str(e))
            return {"error": str(e)}


# Global instance
background_sync_service = BackgroundSyncService()
