"""
Notification schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationSettings(BaseModel):
    """Schema for notification settings"""
    push_enabled: bool = True
    email_enabled: bool = False
    quiet_hours: Optional[Dict[str, Any]] = None
    priority_threshold: int = 50
    categories: Optional[list] = None
    sources: Optional[list] = None
