"""
Premium Subscription Service

Handles premium subscription management, payment processing,
and feature access control for monetization.
"""

import structlog
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
import json
import uuid
import stripe
from enum import Enum

from app.models.user import User, Subscription
from app.core.database import get_db
from app.core.config import settings

logger = structlog.get_logger()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class PremiumService:
    def __init__(self):
        self.subscription_plans = {
            SubscriptionTier.FREE: {
                "name": "Free",
                "price": 0,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "basic_announcements",
                    "basic_search",
                    "email_notifications",
                    "limited_offline_sync"
                ],
                "limits": {
                    "announcements_per_day": 50,
                    "search_queries_per_day": 100,
                    "offline_storage_mb": 10,
                    "push_notifications_per_day": 20
                }
            },
            SubscriptionTier.BASIC: {
                "name": "Basic",
                "price": 9.99,
                "currency": "usd",
                "interval": "month",
                "stripe_price_id": "price_basic_monthly",
                "features": [
                    "unlimited_announcements",
                    "advanced_search",
                    "priority_notifications",
                    "offline_sync",
                    "personalization",
                    "basic_analytics"
                ],
                "limits": {
                    "announcements_per_day": -1,  # unlimited
                    "search_queries_per_day": 500,
                    "offline_storage_mb": 100,
                    "push_notifications_per_day": 100
                }
            },
            SubscriptionTier.PREMIUM: {
                "name": "Premium",
                "price": 19.99,
                "currency": "usd",
                "interval": "month",
                "stripe_price_id": "price_premium_monthly",
                "features": [
                    "unlimited_announcements",
                    "advanced_search",
                    "priority_notifications",
                    "offline_sync",
                    "personalization",
                    "advanced_analytics",
                    "ai_insights",
                    "custom_filters",
                    "export_data",
                    "priority_support"
                ],
                "limits": {
                    "announcements_per_day": -1,
                    "search_queries_per_day": -1,
                    "offline_storage_mb": 500,
                    "push_notifications_per_day": -1
                }
            },
            SubscriptionTier.ENTERPRISE: {
                "name": "Enterprise",
                "price": 99.99,
                "currency": "usd",
                "interval": "month",
                "stripe_price_id": "price_enterprise_monthly",
                "features": [
                    "unlimited_announcements",
                    "advanced_search",
                    "priority_notifications",
                    "offline_sync",
                    "personalization",
                    "advanced_analytics",
                    "ai_insights",
                    "custom_filters",
                    "export_data",
                    "priority_support",
                    "api_access",
                    "custom_integrations",
                    "dedicated_support",
                    "white_label"
                ],
                "limits": {
                    "announcements_per_day": -1,
                    "search_queries_per_day": -1,
                    "offline_storage_mb": -1,
                    "push_notifications_per_day": -1
                }
            }
        }
    
    async def create_subscription(
        self, 
        db: Session, 
        user_id: str, 
        tier: SubscriptionTier,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new premium subscription for a user.
        
        Args:
            user_id: User ID
            tier: Subscription tier
            payment_method_id: Stripe payment method ID
            
        Returns:
            Subscription creation result
        """
        logger.info("Creating premium subscription", 
                   user_id=user_id, 
                   tier=tier.value)
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Check if user already has an active subscription
            existing_subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                Subscription.tier != SubscriptionTier.FREE.value
            ).first()
            
            if existing_subscription:
                return {"error": "User already has an active subscription"}
            
            # Get subscription plan
            plan = self.subscription_plans.get(tier)
            if not plan:
                return {"error": "Invalid subscription tier"}
            
            # Create Stripe customer if not exists
            stripe_customer_id = await self._get_or_create_stripe_customer(user)
            
            # Create Stripe subscription
            stripe_subscription = None
            if tier != SubscriptionTier.FREE:
                stripe_subscription = await self._create_stripe_subscription(
                    stripe_customer_id, 
                    plan, 
                    payment_method_id
                )
            
            # Create local subscription record
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                tier=tier.value,
                status=SubscriptionStatus.ACTIVE.value,
                stripe_subscription_id=stripe_subscription.id if stripe_subscription else None,
                stripe_customer_id=stripe_customer_id,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            # Update user preferences with subscription info
            if not user.preferences:
                user.preferences = {}
            user.preferences["subscription_tier"] = tier.value
            user.preferences["subscription_features"] = plan["features"]
            user.preferences["subscription_limits"] = plan["limits"]
            db.commit()
            
            logger.info("Premium subscription created successfully", 
                       user_id=user_id, 
                       subscription_id=subscription.id,
                       tier=tier.value)
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "tier": tier.value,
                "status": subscription.status,
                "features": plan["features"],
                "limits": plan["limits"],
                "stripe_subscription_id": stripe_subscription.id if stripe_subscription else None
            }
            
        except Exception as e:
            logger.error("Failed to create premium subscription", 
                        user_id=user_id, 
                        tier=tier.value, 
                        error=str(e))
            return {"error": str(e)}
    
    async def cancel_subscription(
        self, 
        db: Session, 
        user_id: str, 
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel a premium subscription.
        
        Args:
            user_id: User ID
            subscription_id: Subscription ID
            immediately: Whether to cancel immediately or at period end
            
        Returns:
            Cancellation result
        """
        logger.info("Cancelling premium subscription", 
                   user_id=user_id, 
                   subscription_id=subscription_id,
                   immediately=immediately)
        
        try:
            subscription = db.query(Subscription).filter(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).first()
            
            if not subscription:
                return {"error": "Subscription not found"}
            
            # Cancel Stripe subscription
            if subscription.stripe_subscription_id:
                if immediately:
                    stripe.Subscription.delete(subscription.stripe_subscription_id)
                else:
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True
                    )
            
            # Update local subscription
            if immediately:
                subscription.status = SubscriptionStatus.CANCELLED.value
                subscription.is_active = False
                subscription.cancelled_at = datetime.utcnow()
            else:
                subscription.cancel_at_period_end = True
                subscription.cancelled_at = datetime.utcnow()
            
            subscription.updated_at = datetime.utcnow()
            db.commit()
            
            # Downgrade user to free tier
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.preferences:
                user.preferences["subscription_tier"] = SubscriptionTier.FREE.value
                user.preferences["subscription_features"] = self.subscription_plans[SubscriptionTier.FREE]["features"]
                user.preferences["subscription_limits"] = self.subscription_plans[SubscriptionTier.FREE]["limits"]
                db.commit()
            
            logger.info("Premium subscription cancelled successfully", 
                       user_id=user_id, 
                       subscription_id=subscription_id)
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "cancelled_immediately": immediately,
                "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None
            }
            
        except Exception as e:
            logger.error("Failed to cancel premium subscription", 
                        user_id=user_id, 
                        subscription_id=subscription_id, 
                        error=str(e))
            return {"error": str(e)}
    
    async def get_subscription_status(
        self, 
        db: Session, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get current subscription status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Subscription status and details
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Get active subscription
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            ).first()
            
            if not subscription:
                # Return free tier status
                free_plan = self.subscription_plans[SubscriptionTier.FREE]
                return {
                    "tier": SubscriptionTier.FREE.value,
                    "status": "active",
                    "features": free_plan["features"],
                    "limits": free_plan["limits"],
                    "is_premium": False,
                    "subscription_id": None
                }
            
            # Get plan details
            plan = self.subscription_plans.get(SubscriptionTier(subscription.tier))
            
            return {
                "tier": subscription.tier,
                "status": subscription.status,
                "features": plan["features"] if plan else [],
                "limits": plan["limits"] if plan else {},
                "is_premium": subscription.tier != SubscriptionTier.FREE.value,
                "subscription_id": subscription.id,
                "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
            
        except Exception as e:
            logger.error("Failed to get subscription status", 
                        user_id=user_id, 
                        error=str(e))
            return {"error": str(e)}
    
    async def check_feature_access(
        self, 
        db: Session, 
        user_id: str, 
        feature: str
    ) -> bool:
        """
        Check if user has access to a specific feature.
        
        Args:
            user_id: User ID
            feature: Feature name
            
        Returns:
            Whether user has access to the feature
        """
        try:
            status = await self.get_subscription_status(db, user_id)
            if "error" in status:
                return False
            
            features = status.get("features", [])
            return feature in features
            
        except Exception as e:
            logger.error("Failed to check feature access", 
                        user_id=user_id, 
                        feature=feature, 
                        error=str(e))
            return False
    
    async def check_usage_limit(
        self, 
        db: Session, 
        user_id: str, 
        limit_type: str,
        current_usage: int
    ) -> Dict[str, Any]:
        """
        Check if user is within usage limits.
        
        Args:
            user_id: User ID
            limit_type: Type of limit to check
            current_usage: Current usage count
            
        Returns:
            Limit check result
        """
        try:
            status = await self.get_subscription_status(db, user_id)
            if "error" in status:
                return {"error": "Failed to get subscription status"}
            
            limits = status.get("limits", {})
            limit_value = limits.get(limit_type, 0)
            
            # -1 means unlimited
            if limit_value == -1:
                return {
                    "within_limit": True,
                    "limit": -1,
                    "current_usage": current_usage,
                    "remaining": -1
                }
            
            within_limit = current_usage < limit_value
            remaining = max(0, limit_value - current_usage) if limit_value > 0 else 0
            
            return {
                "within_limit": within_limit,
                "limit": limit_value,
                "current_usage": current_usage,
                "remaining": remaining
            }
            
        except Exception as e:
            logger.error("Failed to check usage limit", 
                        user_id=user_id, 
                        limit_type=limit_type, 
                        error=str(e))
            return {"error": str(e)}
    
    async def _get_or_create_stripe_customer(self, user: User) -> str:
        """Get or create Stripe customer for user."""
        try:
            if user.stripe_customer_id:
                return user.stripe_customer_id
            
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    "user_id": str(user.id),
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
            )
            
            # Update user with Stripe customer ID
            user.stripe_customer_id = customer.id
            db = get_db()
            db.commit()
            
            return customer.id
            
        except Exception as e:
            logger.error("Failed to create Stripe customer", 
                        user_id=str(user.id), 
                        error=str(e))
            raise
    
    async def _create_stripe_subscription(
        self, 
        customer_id: str, 
        plan: Dict[str, Any], 
        payment_method_id: Optional[str]
    ) -> stripe.Subscription:
        """Create Stripe subscription."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": plan["stripe_price_id"]}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"]
            }
            
            if payment_method_id:
                subscription_data["default_payment_method"] = payment_method_id
            
            subscription = stripe.Subscription.create(**subscription_data)
            return subscription
            
        except Exception as e:
            logger.error("Failed to create Stripe subscription", 
                        customer_id=customer_id, 
                        error=str(e))
            raise
    
    async def get_available_plans(self) -> List[Dict[str, Any]]:
        """Get all available subscription plans."""
        return [
            {
                "tier": tier.value,
                "name": plan["name"],
                "price": plan["price"],
                "currency": plan["currency"],
                "interval": plan["interval"],
                "features": plan["features"],
                "limits": plan["limits"]
            }
            for tier, plan in self.subscription_plans.items()
        ]


# Global instance
premium_service = PremiumService()
