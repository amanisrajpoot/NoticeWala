"""
Subscription schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SubscriptionFilters(BaseModel):
    """Schema for subscription filters"""
    categories: Optional[list] = None
    keywords: Optional[list] = None
    locations: Optional[list] = None
    sources: Optional[list] = None
    date_range: Optional[Dict[str, str]] = None
    min_priority: Optional[float] = None


class QuietHours(BaseModel):
    """Schema for quiet hours configuration"""
    enabled: bool = False
    start_time: str = "22:00"  # HH:MM format
    end_time: str = "08:00"    # HH:MM format
    timezone: str = "UTC"


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    name: str
    filters: SubscriptionFilters
    notification_enabled: bool = True
    quiet_hours: Optional[QuietHours] = None
    priority_threshold: int = 50


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    name: Optional[str] = None
    filters: Optional[SubscriptionFilters] = None
    is_active: Optional[bool] = None
    notification_enabled: Optional[bool] = None
    quiet_hours: Optional[QuietHours] = None
    priority_threshold: Optional[int] = None


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: str
    name: str
    filters: SubscriptionFilters
    is_active: bool
    notification_enabled: bool
    priority_threshold: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
