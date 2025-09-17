"""
User schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class PushTokenCreate(BaseModel):
    """Schema for push token registration"""
    token: str
    platform: str  # ios, android, web
    device_id: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None


class UserPreferences(BaseModel):
    """Schema for user preferences"""
    language: str = "en"
    timezone: str = "UTC"
    notification_frequency: str = "immediate"  # immediate, daily, weekly
    categories: Optional[list] = None
    regions: Optional[list] = None
    keywords: Optional[list] = None


class NotificationSettings(BaseModel):
    """Schema for notification settings"""
    push_enabled: bool = True
    email_enabled: bool = False
    quiet_hours: Optional[Dict[str, Any]] = None
    priority_threshold: int = 50
    categories: Optional[list] = None
    sources: Optional[list] = None
