"""
Notification Celery Tasks for NoticeWala Backend
"""

from celery import current_task
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.database import engine
from app.core.celery_app import celery_app
from app.services.notification_service import notification_service
from app.models.announcement import Announcement

logger = structlog.get_logger()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_announcement_notifications")
def send_announcement_notifications(self, announcement_id: str):
    """Send notifications for a new announcement"""
    
    db = SessionLocal()
    try:
        logger.info("Starting announcement notification task", announcement_id=announcement_id)
        
        # Get announcement
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            logger.error("Announcement not found", announcement_id=announcement_id)
            return {"status": "error", "message": "Announcement not found"}
        
        # Send notifications
        sent_count = await notification_service.send_announcement_notifications(
            announcement, db
        )
        
        logger.info(
            "Announcement notification task completed",
            announcement_id=announcement_id,
            sent_count=sent_count
        )
        
        return {
            "status": "success",
            "announcement_id": announcement_id,
            "notifications_sent": sent_count
        }
        
    except Exception as e:
        logger.error(
            "Error in announcement notification task",
            announcement_id=announcement_id,
            error=str(e)
        )
        raise self.retry(countdown=60, max_retries=3)
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_deadline_reminders")
def send_deadline_reminders(self):
    """Send deadline reminder notifications"""
    
    db = SessionLocal()
    try:
        logger.info("Starting deadline reminders task")
        
        # Send deadline reminders
        sent_count = await notification_service.send_deadline_reminders(db)
        
        logger.info(
            "Deadline reminders task completed",
            sent_count=sent_count
        )
        
        return {
            "status": "success",
            "reminders_sent": sent_count
        }
        
    except Exception as e:
        logger.error("Error in deadline reminders task", error=str(e))
        raise self.retry(countdown=300, max_retries=2)
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_custom_notification")
def send_custom_notification(
    self,
    user_id: str,
    title: str,
    body: str,
    data: dict = None
):
    """Send a custom notification to a specific user"""
    
    db = SessionLocal()
    try:
        logger.info("Starting custom notification task", user_id=user_id)
        
        # Send notification
        success = await notification_service.send_push_notification(
            user_id=user_id,
            title=title,
            body=body,
            data=data or {},
            db=db
        )
        
        if success:
            logger.info("Custom notification sent successfully", user_id=user_id)
            return {"status": "success", "message": "Notification sent"}
        else:
            logger.warning("Custom notification failed", user_id=user_id)
            return {"status": "error", "message": "Notification failed"}
        
    except Exception as e:
        logger.error(
            "Error in custom notification task",
            user_id=user_id,
            error=str(e)
        )
        raise self.retry(countdown=60, max_retries=3)
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.notification_tasks.bulk_notification")
def bulk_notification(
    self,
    user_ids: list,
    title: str,
    body: str,
    data: dict = None
):
    """Send bulk notifications to multiple users"""
    
    db = SessionLocal()
    try:
        logger.info("Starting bulk notification task", user_count=len(user_ids))
        
        sent_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                success = await notification_service.send_push_notification(
                    user_id=user_id,
                    title=title,
                    body=body,
                    data=data or {},
                    db=db
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(
                    "Error sending notification to user",
                    user_id=user_id,
                    error=str(e)
                )
                failed_count += 1
        
        logger.info(
            "Bulk notification task completed",
            sent_count=sent_count,
            failed_count=failed_count,
            total=len(user_ids)
        )
        
        return {
            "status": "completed",
            "sent": sent_count,
            "failed": failed_count,
            "total": len(user_ids)
        }
        
    except Exception as e:
        logger.error("Error in bulk notification task", error=str(e))
        raise self.retry(countdown=300, max_retries=2)
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.notification_tasks.process_notification_queue")
def process_notification_queue(self):
    """Process pending notifications from queue"""
    
    db = SessionLocal()
    try:
        logger.info("Starting notification queue processing")
        
        # This would typically process a queue of pending notifications
        # For now, it's a placeholder for future queue-based processing
        
        logger.info("Notification queue processing completed")
        
        return {
            "status": "success",
            "message": "Queue processed"
        }
        
    except Exception as e:
        logger.error("Error in notification queue processing", error=str(e))
        raise self.retry(countdown=60, max_retries=3)
    finally:
        db.close()
