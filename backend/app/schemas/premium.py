"""
Pydantic schemas for premium subscription functionality.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


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


class CreateSubscriptionRequest(BaseModel):
    """Request schema for creating a subscription."""
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    trial_period_days: Optional[int] = Field(None, description="Trial period in days")


class CreateSubscriptionResponse(BaseModel):
    """Response schema for subscription creation."""
    success: bool = Field(..., description="Whether the subscription was created successfully")
    subscription_id: str = Field(..., description="ID of the created subscription")
    tier: str = Field(..., description="Subscription tier")
    status: str = Field(..., description="Subscription status")
    features: List[str] = Field(..., description="Available features")
    limits: Dict[str, Any] = Field(..., description="Usage limits")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")


class CancelSubscriptionRequest(BaseModel):
    """Request schema for cancelling a subscription."""
    subscription_id: str = Field(..., description="ID of the subscription to cancel")
    immediately: bool = Field(False, description="Whether to cancel immediately or at period end")
    reason: Optional[str] = Field(None, description="Cancellation reason")


class CancelSubscriptionResponse(BaseModel):
    """Response schema for subscription cancellation."""
    success: bool = Field(..., description="Whether the subscription was cancelled successfully")
    subscription_id: str = Field(..., description="ID of the cancelled subscription")
    cancelled_immediately: bool = Field(..., description="Whether cancelled immediately")
    cancelled_at: Optional[str] = Field(None, description="Cancellation timestamp")


class SubscriptionStatusResponse(BaseModel):
    """Response schema for subscription status."""
    tier: str = Field(..., description="Current subscription tier")
    status: str = Field(..., description="Subscription status")
    features: List[str] = Field(..., description="Available features")
    limits: Dict[str, Any] = Field(..., description="Usage limits")
    is_premium: bool = Field(..., description="Whether user has premium subscription")
    subscription_id: Optional[str] = Field(None, description="Subscription ID")
    current_period_start: Optional[str] = Field(None, description="Current period start")
    current_period_end: Optional[str] = Field(None, description="Current period end")
    cancel_at_period_end: Optional[bool] = Field(None, description="Whether set to cancel at period end")


class FeatureAccessResponse(BaseModel):
    """Response schema for feature access check."""
    feature: str = Field(..., description="Feature name")
    has_access: bool = Field(..., description="Whether user has access to the feature")
    user_id: str = Field(..., description="User ID")


class UsageLimitResponse(BaseModel):
    """Response schema for usage limit check."""
    limit_type: str = Field(..., description="Type of usage limit")
    user_id: str = Field(..., description="User ID")
    within_limit: bool = Field(..., description="Whether within usage limit")
    limit: int = Field(..., description="Usage limit (-1 for unlimited)")
    current_usage: int = Field(..., description="Current usage count")
    remaining: int = Field(..., description="Remaining usage (-1 for unlimited)")


class SubscriptionPlan(BaseModel):
    """Schema for a subscription plan."""
    tier: str = Field(..., description="Plan tier")
    name: str = Field(..., description="Plan name")
    price: float = Field(..., description="Plan price")
    currency: str = Field(..., description="Currency")
    interval: str = Field(..., description="Billing interval")
    features: List[str] = Field(..., description="Plan features")
    limits: Dict[str, Any] = Field(..., description="Usage limits")


class SubscriptionPlansResponse(BaseModel):
    """Response schema for subscription plans."""
    plans: List[SubscriptionPlan] = Field(..., description="Available subscription plans")
    total_count: int = Field(..., description="Total number of plans")


class PaymentMethod(BaseModel):
    """Schema for payment method information."""
    id: str = Field(..., description="Payment method ID")
    type: str = Field(..., description="Payment method type")
    card_last4: Optional[str] = Field(None, description="Last 4 digits of card")
    card_brand: Optional[str] = Field(None, description="Card brand")
    exp_month: Optional[int] = Field(None, description="Expiration month")
    exp_year: Optional[int] = Field(None, description="Expiration year")


class BillingInfo(BaseModel):
    """Schema for billing information."""
    customer_id: str = Field(..., description="Stripe customer ID")
    payment_methods: List[PaymentMethod] = Field(default_factory=list, description="Payment methods")
    default_payment_method: Optional[str] = Field(None, description="Default payment method ID")
    billing_address: Optional[Dict[str, Any]] = Field(None, description="Billing address")


class Invoice(BaseModel):
    """Schema for invoice information."""
    id: str = Field(..., description="Invoice ID")
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(..., description="Currency")
    status: str = Field(..., description="Invoice status")
    created_at: datetime = Field(..., description="Invoice creation date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    paid_at: Optional[datetime] = Field(None, description="Payment date")
    invoice_url: Optional[str] = Field(None, description="Invoice URL")


class BillingHistoryResponse(BaseModel):
    """Response schema for billing history."""
    invoices: List[Invoice] = Field(..., description="Invoice history")
    total_count: int = Field(..., description="Total number of invoices")
    has_more: bool = Field(False, description="Whether there are more invoices")


class UpgradeRequest(BaseModel):
    """Request schema for subscription upgrade."""
    target_tier: SubscriptionTier = Field(..., description="Target subscription tier")
    prorate: bool = Field(True, description="Whether to prorate the upgrade")
    payment_method_id: Optional[str] = Field(None, description="Payment method for upgrade")


class UpgradeResponse(BaseModel):
    """Response schema for subscription upgrade."""
    success: bool = Field(..., description="Whether the upgrade was successful")
    old_tier: str = Field(..., description="Previous subscription tier")
    new_tier: str = Field(..., description="New subscription tier")
    prorated_amount: Optional[int] = Field(None, description="Prorated amount in cents")
    effective_date: str = Field(..., description="Effective date of upgrade")


class DowngradeRequest(BaseModel):
    """Request schema for subscription downgrade."""
    target_tier: SubscriptionTier = Field(..., description="Target subscription tier")
    effective_date: Optional[datetime] = Field(None, description="Effective date for downgrade")


class DowngradeResponse(BaseModel):
    """Response schema for subscription downgrade."""
    success: bool = Field(..., description="Whether the downgrade was successful")
    old_tier: str = Field(..., description="Previous subscription tier")
    new_tier: str = Field(..., description="New subscription tier")
    effective_date: str = Field(..., description="Effective date of downgrade")


class UsageStats(BaseModel):
    """Schema for usage statistics."""
    limit_type: str = Field(..., description="Type of usage limit")
    current_usage: int = Field(..., description="Current usage count")
    limit: int = Field(..., description="Usage limit (-1 for unlimited)")
    percentage_used: float = Field(..., description="Percentage of limit used")
    reset_date: Optional[datetime] = Field(None, description="Date when usage resets")


class UsageStatsResponse(BaseModel):
    """Response schema for usage statistics."""
    stats: List[UsageStats] = Field(..., description="Usage statistics")
    period_start: datetime = Field(..., description="Start of current period")
    period_end: datetime = Field(..., description="End of current period")


class FeatureLimit(BaseModel):
    """Schema for feature limits."""
    feature: str = Field(..., description="Feature name")
    limit: int = Field(..., description="Feature limit (-1 for unlimited)")
    current_usage: int = Field(..., description="Current usage")
    remaining: int = Field(..., description="Remaining usage")


class FeatureLimitsResponse(BaseModel):
    """Response schema for feature limits."""
    limits: List[FeatureLimit] = Field(..., description="Feature limits")
    tier: str = Field(..., description="Current subscription tier")


class WebhookEvent(BaseModel):
    """Schema for webhook events."""
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    created: datetime = Field(..., description="Event creation time")
    data: Dict[str, Any] = Field(..., description="Event data")
    livemode: bool = Field(..., description="Whether in live mode")


class WebhookResponse(BaseModel):
    """Response schema for webhook processing."""
    status: str = Field(..., description="Processing status")
    event_id: str = Field(..., description="Event ID")
    processed_at: datetime = Field(..., description="Processing time")
