"""
Notification Service for NoticeWala Backend
Handles push notifications, email notifications, and notification management
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Subscription, Notification, PushToken
from app.models.announcement import Announcement

logger = structlog.get_logger()


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.fcm_enabled = bool(settings.FCM_SERVER_KEY)
        
    async def send_push_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> bool:
        """Send push notification to user"""
        
        try:
            # Get user's push tokens
            push_tokens = db.query(PushToken).filter(
                and_(
                    PushToken.user_id == user_id,
                    PushToken.is_active == True
                )
            ).all()
            
            if not push_tokens:
                logger.warning("No active push tokens found for user", user_id=user_id)
                return False
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                title=title,
                body=body,
                data=data or {},
                status="pending"
            )
            db.add(notification)
            db.commit()
            
            # Send to each push token
            success_count = 0
            for token in push_tokens:
                try:
                    success = await self._send_fcm_notification(
                        token.token,
                        token.platform,
                        title,
                        body,
                        data
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(
                            "Push notification sent successfully",
                            user_id=user_id,
                            platform=token.platform
                        )
                    else:
                        logger.warning(
                            "Failed to send push notification",
                            user_id=user_id,
                            platform=token.platform
                        )
                        
                except Exception as e:
                    logger.error(
                        "Error sending push notification",
                        user_id=user_id,
                        platform=token.platform,
                        error=str(e)
                    )
            
            # Update notification status
            if success_count > 0:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
                db.commit()
                return True
            else:
                notification.status = "failed"
                notification.error_message = "All push tokens failed"
                db.commit()
                return False
                
        except Exception as e:
            logger.error("Error in send_push_notification", error=str(e))
            return False
    
    async def _send_fcm_notification(
        self,
        token: str,
        platform: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send FCM notification (placeholder implementation)"""
        
        if not self.fcm_enabled:
            logger.warning("FCM not enabled, skipping push notification")
            return False
        
        try:
            # TODO: Implement actual FCM sending
            # This would use firebase-admin SDK or HTTP requests to FCM
            
            # Placeholder implementation
            logger.info(
                "FCM notification would be sent",
                token=token[:10] + "...",
                platform=platform,
                title=title
            )
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # For now, always return success
            return True
            
        except Exception as e:
            logger.error("FCM notification failed", error=str(e))
            return False
    
    async def send_announcement_notifications(
        self,
        announcement: Announcement,
        db: Session
    ) -> int:
        """Send notifications for a new announcement to matching subscriptions"""
        
        try:
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(
                announcement, db
            )
            
            if not matching_subscriptions:
                logger.info("No matching subscriptions found for announcement")
                return 0
            
            # Send notifications
            sent_count = 0
            for subscription in matching_subscriptions:
                try:
                    # Check if user wants notifications for this priority
                    if announcement.priority_score < (subscription.priority_threshold / 100):
                        continue
                    
                    # Prepare notification content
                    title = f"New: {announcement.title[:50]}..."
                    
                    body = announcement.summary or announcement.title
                    if len(body) > 100:
                        body = body[:97] + "..."
                    
                    data = {
                        "announcement_id": str(announcement.id),
                        "type": "exam_notification",
                        "priority": "high" if announcement.priority_score > 0.7 else "medium"
                    }
                    
                    # Send notification
                    success = await self.send_push_notification(
                        subscription.user_id,
                        title,
                        body,
                        data,
                        db
                    )
                    
                    if success:
                        sent_count += 1
                        # Update subscription stats
                        subscription.notification_count += 1
                        subscription.last_notified = datetime.utcnow()
                        
                except Exception as e:
                    logger.error(
                        "Error sending notification to subscription",
                        subscription_id=str(subscription.id),
                        error=str(e)
                    )
            
            db.commit()
            logger.info(
                "Announcement notifications sent",
                announcement_id=str(announcement.id),
                sent_count=sent_count,
                total_subscriptions=len(matching_subscriptions)
            )
            
            return sent_count
            
        except Exception as e:
            logger.error("Error in send_announcement_notifications", error=str(e))
            return 0
    
    def _find_matching_subscriptions(
        self,
        announcement: Announcement,
        db: Session
    ) -> List[Subscription]:
        """Find subscriptions that match the announcement"""
        
        try:
            query = db.query(Subscription).filter(
                and_(
                    Subscription.is_active == True,
                    Subscription.notification_enabled == True
                )
            )
            
            matching_subscriptions = []
            
            for subscription in query.all():
                if self._subscription_matches_announcement(subscription, announcement):
                    matching_subscriptions.append(subscription)
            
            return matching_subscriptions
            
        except Exception as e:
            logger.error("Error finding matching subscriptions", error=str(e))
            return []
    
    def _subscription_matches_announcement(
        self,
        subscription: Subscription,
        announcement: Announcement
    ) -> bool:
        """Check if subscription matches announcement"""
        
        try:
            filters = subscription.filters or {}
            
            # Check categories
            if filters.get('categories'):
                announcement_categories = set(announcement.categories or [])
                subscription_categories = set(filters['categories'])
                if not announcement_categories.intersection(subscription_categories):
                    return False
            
            # Check keywords
            if filters.get('keywords'):
                text_to_search = f"{announcement.title} {announcement.summary or ''} {announcement.content or ''}".lower()
                subscription_keywords = [kw.lower() for kw in filters['keywords']]
                if not any(keyword in text_to_search for keyword in subscription_keywords):
                    return False
            
            # Check locations
            if filters.get('locations'):
                announcement_location = announcement.location or {}
                announcement_regions = set()
                
                if announcement_location.get('country'):
                    announcement_regions.add(announcement_location['country'].lower())
                if announcement_location.get('state'):
                    announcement_regions.add(announcement_location['state'].lower())
                if announcement_location.get('city'):
                    announcement_regions.add(announcement_location['city'].lower())
                
                subscription_locations = {loc.lower() for loc in filters['locations']}
                if not announcement_regions.intersection(subscription_locations):
                    return False
            
            # Check sources
            if filters.get('sources'):
                if str(announcement.source_id) not in filters['sources']:
                    return False
            
            # Check date range
            if filters.get('date_range'):
                date_range = filters['date_range']
                if announcement.publish_date:
                    publish_date = announcement.publish_date.date()
                    if date_range.get('from'):
                        from_date = datetime.strptime(date_range['from'], '%Y-%m-%d').date()
                        if publish_date < from_date:
                            return False
                    if date_range.get('to'):
                        to_date = datetime.strptime(date_range['to'], '%Y-%m-%d').date()
                        if publish_date > to_date:
                            return False
            
            # Check minimum priority
            min_priority = filters.get('min_priority', 0)
            if announcement.priority_score < (min_priority / 100):
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking subscription match", error=str(e))
            return False
    
    async def send_deadline_reminders(self, db: Session) -> int:
        """Send deadline reminder notifications"""
        
        try:
            # Find announcements with deadlines in the next 7 days
            today = datetime.utcnow().date()
            reminder_date = today + timedelta(days=7)
            
            announcements = db.query(Announcement).filter(
                and_(
                    Announcement.application_deadline.isnot(None),
                    Announcement.application_deadline >= today,
                    Announcement.application_deadline <= reminder_date,
                    Announcement.is_duplicate == False
                )
            ).all()
            
            sent_count = 0
            
            for announcement in announcements:
                try:
                    # Find subscriptions that might be interested
                    matching_subscriptions = self._find_matching_subscriptions(
                        announcement, db
                    )
                    
                    for subscription in matching_subscriptions:
                        # Check if we should send reminder (not sent recently)
                        if subscription.last_notified:
                            time_since_last = datetime.utcnow() - subscription.last_notified
                            if time_since_last < timedelta(hours=24):
                                continue
                        
                        # Prepare reminder message
                        days_left = (announcement.application_deadline.date() - today).days
                        
                        if days_left == 0:
                            title = "⚠️ Deadline Today!"
                            body = f"{announcement.title} - Application deadline is today!"
                        elif days_left == 1:
                            title = "⏰ Deadline Tomorrow"
                            body = f"{announcement.title} - Application deadline is tomorrow!"
                        else:
                            title = f"📅 {days_left} Days Left"
                            body = f"{announcement.title} - Application deadline in {days_left} days"
                        
                        data = {
                            "announcement_id": str(announcement.id),
                            "type": "deadline_reminder",
                            "days_left": days_left
                        }
                        
                        # Send notification
                        success = await self.send_push_notification(
                            subscription.user_id,
                            title,
                            body,
                            data,
                            db
                        )
                        
                        if success:
                            sent_count += 1
                            
                except Exception as e:
                    logger.error(
                        "Error sending deadline reminder",
                        announcement_id=str(announcement.id),
                        error=str(e)
                    )
            
            logger.info(
                "Deadline reminders sent",
                sent_count=sent_count,
                total_announcements=len(announcements)
            )
            
            return sent_count
            
        except Exception as e:
            logger.error("Error in send_deadline_reminders", error=str(e))
            return 0
    
    def get_notification_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get notification statistics for user"""
        
        try:
            # Get total notifications
            total_notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).count()
            
            # Get unread notifications
            unread_notifications = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.opened_at.is_(None)
                )
            ).count()
            
            # Get notifications by status
            sent_notifications = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.status == "sent"
                )
            ).count()
            
            failed_notifications = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.status == "failed"
                )
            ).count()
            
            return {
                "total": total_notifications,
                "unread": unread_notifications,
                "sent": sent_notifications,
                "failed": failed_notifications,
                "delivery_rate": (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0
            }
            
        except Exception as e:
            logger.error("Error getting notification stats", error=str(e))
            return {
                "total": 0,
                "unread": 0,
                "sent": 0,
                "failed": 0,
                "delivery_rate": 0
            }


# Create singleton instance
notification_service = NotificationService()
