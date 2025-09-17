"""
Notifications API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import Notification, PushToken
from app.schemas.notification import NotificationResponse, NotificationSettings

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's notifications"""
    
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user_id)
        
        if status_filter:
            query = query.filter(Notification.status == status_filter)
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        notification_list = []
        for notif in notifications:
            notification_list.append(NotificationResponse(
                id=str(notif.id),
                title=notif.title,
                body=notif.body,
                data=notif.data,
                status=notif.status,
                created_at=notif.created_at,
                sent_at=notif.sent_at,
                delivered_at=notif.delivered_at,
                opened_at=notif.opened_at
            ))
        
        logger.info(
            "User notifications retrieved",
            user_id=current_user_id,
            count=len(notifications),
            status_filter=status_filter
        )
        
        return notification_list
        
    except Exception as e:
        logger.error("Failed to retrieve user notifications", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.opened_at = db.func.now()
        db.commit()
        
        logger.info("Notification marked as read", user_id=current_user_id, notification_id=notification_id)
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to mark notification as read", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        logger.info("Notification deleted", user_id=current_user_id, notification_id=notification_id)
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete notification", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )


@router.get("/settings")
async def get_notification_settings(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's notification settings"""
    
    try:
        # Get user's push tokens to check if notifications are enabled
        push_tokens = db.query(PushToken).filter(
            PushToken.user_id == current_user_id,
            PushToken.is_active == True
        ).all()
        
        settings = {
            "push_enabled": len(push_tokens) > 0,
            "active_tokens": len(push_tokens),
            "platforms": list(set(token.platform for token in push_tokens))
        }
        
        logger.info("Notification settings retrieved", user_id=current_user_id)
        
        return settings
        
    except Exception as e:
        logger.error("Failed to retrieve notification settings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification settings"
        )
