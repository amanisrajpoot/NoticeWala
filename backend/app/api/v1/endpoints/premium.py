"""
Premium Subscription API Endpoints

Handles premium subscription management, payment processing,
and feature access control for monetization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.premium_service import premium_service, SubscriptionTier, SubscriptionStatus
from app.schemas.premium import (
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    CancelSubscriptionRequest,
    CancelSubscriptionResponse,
    SubscriptionStatusResponse,
    FeatureAccessResponse,
    UsageLimitResponse,
    SubscriptionPlansResponse
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/subscribe", response_model=CreateSubscriptionResponse)
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Create a new premium subscription for the current user.
    """
    try:
        logger.info("Creating premium subscription", 
                   user_id=current_user_id, 
                   tier=request.tier)
        
        result = await premium_service.create_subscription(
            db=db,
            user_id=current_user_id,
            tier=SubscriptionTier(request.tier),
            payment_method_id=request.payment_method_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return CreateSubscriptionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create subscription", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Cancel the current user's premium subscription.
    """
    try:
        logger.info("Cancelling premium subscription", 
                   user_id=current_user_id, 
                   subscription_id=request.subscription_id)
        
        result = await premium_service.cancel_subscription(
            db=db,
            user_id=current_user_id,
            subscription_id=request.subscription_id,
            immediately=request.immediately
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return CancelSubscriptionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel subscription", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Get the current user's subscription status and details.
    """
    try:
        result = await premium_service.get_subscription_status(
            db=db,
            user_id=current_user_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return SubscriptionStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get subscription status", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )


@router.get("/feature-access/{feature}", response_model=FeatureAccessResponse)
async def check_feature_access(
    feature: str,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Check if the current user has access to a specific feature.
    """
    try:
        has_access = await premium_service.check_feature_access(
            db=db,
            user_id=current_user_id,
            feature=feature
        )
        
        return FeatureAccessResponse(
            feature=feature,
            has_access=has_access,
            user_id=current_user_id
        )
        
    except Exception as e:
        logger.error("Failed to check feature access", 
                    user_id=current_user_id, 
                    feature=feature, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check feature access: {str(e)}"
        )


@router.get("/usage-limit/{limit_type}", response_model=UsageLimitResponse)
async def check_usage_limit(
    limit_type: str,
    current_usage: int = Query(0, description="Current usage count"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Check if the current user is within usage limits for a specific limit type.
    """
    try:
        result = await premium_service.check_usage_limit(
            db=db,
            user_id=current_user_id,
            limit_type=limit_type,
            current_usage=current_usage
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return UsageLimitResponse(
            limit_type=limit_type,
            user_id=current_user_id,
            **result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check usage limit", 
                    user_id=current_user_id, 
                    limit_type=limit_type, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check usage limit: {str(e)}"
        )


@router.get("/plans", response_model=SubscriptionPlansResponse)
async def get_subscription_plans():
    """
    Get all available subscription plans.
    """
    try:
        plans = await premium_service.get_available_plans()
        
        return SubscriptionPlansResponse(
            plans=plans,
            total_count=len(plans)
        )
        
    except Exception as e:
        logger.error("Failed to get subscription plans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events for subscription updates.
    """
    try:
        # This would typically verify the webhook signature
        # and process the event based on its type
        
        event_type = request.get("type")
        data = request.get("data", {})
        
        logger.info("Received Stripe webhook", event_type=event_type)
        
        if event_type == "customer.subscription.updated":
            await _handle_subscription_updated(db, data)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(db, data)
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(db, data)
        elif event_type == "invoice.payment_succeeded":
            await _handle_payment_succeeded(db, data)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error("Failed to process Stripe webhook", 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


async def _handle_subscription_updated(db: Session, data: dict):
    """Handle subscription updated webhook."""
    try:
        subscription_data = data.get("object", {})
        stripe_subscription_id = subscription_data.get("id")
        
        # Find local subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription:
            subscription.status = subscription_data.get("status")
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data.get("current_period_start")
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data.get("current_period_end")
            )
            subscription.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Subscription updated from webhook", 
                       subscription_id=subscription.id,
                       status=subscription.status)
    
    except Exception as e:
        logger.error("Failed to handle subscription updated webhook", error=str(e))


async def _handle_subscription_deleted(db: Session, data: dict):
    """Handle subscription deleted webhook."""
    try:
        subscription_data = data.get("object", {})
        stripe_subscription_id = subscription_data.get("id")
        
        # Find and deactivate local subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED.value
            subscription.is_active = False
            subscription.cancelled_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Subscription cancelled from webhook", 
                       subscription_id=subscription.id)
    
    except Exception as e:
        logger.error("Failed to handle subscription deleted webhook", error=str(e))


async def _handle_payment_failed(db: Session, data: dict):
    """Handle payment failed webhook."""
    try:
        invoice_data = data.get("object", {})
        stripe_subscription_id = invoice_data.get("subscription")
        
        if stripe_subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE.value
                subscription.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info("Payment failed for subscription", 
                           subscription_id=subscription.id)
    
    except Exception as e:
        logger.error("Failed to handle payment failed webhook", error=str(e))


async def _handle_payment_succeeded(db: Session, data: dict):
    """Handle payment succeeded webhook."""
    try:
        invoice_data = data.get("object", {})
        stripe_subscription_id = invoice_data.get("subscription")
        
        if stripe_subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE.value
                subscription.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info("Payment succeeded for subscription", 
                           subscription_id=subscription.id)
    
    except Exception as e:
        logger.error("Failed to handle payment succeeded webhook", error=str(e))


@router.get("/health")
async def premium_health_check():
    """
    Health check for premium service.
    """
    return {
        "status": "healthy",
        "service": "premium",
        "timestamp": datetime.utcnow().isoformat()
    }
