"""
Subscriptions API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's subscriptions"""
    
    try:
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == current_user_id
        ).all()
        
        subscription_list = []
        for sub in subscriptions:
            subscription_list.append(SubscriptionResponse(
                id=str(sub.id),
                name=sub.name,
                filters=sub.filters,
                is_active=sub.is_active,
                notification_enabled=sub.notification_enabled,
                priority_threshold=sub.priority_threshold,
                created_at=sub.created_at,
                updated_at=sub.updated_at
            ))
        
        logger.info("User subscriptions retrieved", user_id=current_user_id, count=len(subscriptions))
        return subscription_list
        
    except Exception as e:
        logger.error("Failed to retrieve user subscriptions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscriptions"
        )


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new subscription"""
    
    try:
        subscription = Subscription(
            user_id=current_user_id,
            name=subscription_data.name,
            filters=subscription_data.filters,
            notification_enabled=subscription_data.notification_enabled,
            quiet_hours=subscription_data.quiet_hours,
            priority_threshold=subscription_data.priority_threshold
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info("Subscription created", user_id=current_user_id, subscription_id=str(subscription.id))
        
        return SubscriptionResponse(
            id=str(subscription.id),
            name=subscription.name,
            filters=subscription.filters,
            is_active=subscription.is_active,
            notification_enabled=subscription.notification_enabled,
            priority_threshold=subscription.priority_threshold,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except Exception as e:
        logger.error("Failed to create subscription", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    subscription_update: SubscriptionUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a subscription"""
    
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Update fields if provided
        if subscription_update.name is not None:
            subscription.name = subscription_update.name
        if subscription_update.filters is not None:
            subscription.filters = subscription_update.filters
        if subscription_update.is_active is not None:
            subscription.is_active = subscription_update.is_active
        if subscription_update.notification_enabled is not None:
            subscription.notification_enabled = subscription_update.notification_enabled
        if subscription_update.quiet_hours is not None:
            subscription.quiet_hours = subscription_update.quiet_hours
        if subscription_update.priority_threshold is not None:
            subscription.priority_threshold = subscription_update.priority_threshold
        
        db.commit()
        db.refresh(subscription)
        
        logger.info("Subscription updated", user_id=current_user_id, subscription_id=subscription_id)
        
        return SubscriptionResponse(
            id=str(subscription.id),
            name=subscription.name,
            filters=subscription.filters,
            is_active=subscription.is_active,
            notification_enabled=subscription.notification_enabled,
            priority_threshold=subscription.priority_threshold,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update subscription", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a subscription"""
    
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.user_id == current_user_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        db.delete(subscription)
        db.commit()
        
        logger.info("Subscription deleted", user_id=current_user_id, subscription_id=subscription_id)
        
        return {"message": "Subscription deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete subscription", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subscription"
        )
