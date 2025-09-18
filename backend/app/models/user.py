"""
User and subscription database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model for managing app users"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON)  # User preferences and settings
    notification_settings = Column(JSON)  # Notification preferences
    
    # Payment integration
    stripe_customer_id = Column(String(255), unique=True, index=True)
    
    # Metadata
    last_login = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    push_tokens = relationship("PushToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Subscription(Base):
    """User subscription model for filtering announcements and premium subscriptions"""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id"), nullable=True)
    
    # Subscription filters (for announcement filtering)
    name = Column(String(200), nullable=False)  # User-defined name for subscription
    filters = Column(JSON)  # Filter criteria (categories, keywords, locations, etc.)
    
    # Premium subscription fields
    tier = Column(String(50), default="free")  # free, basic, premium, enterprise
    status = Column(String(50), default="active")  # active, cancelled, past_due, unpaid, trialing
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)
    
    # Billing information
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True))
    
    # Notification settings
    is_active = Column(Boolean, default=True)
    notification_enabled = Column(Boolean, default=True)
    quiet_hours = Column(JSON)  # Quiet hours configuration
    
    # Metadata
    priority_threshold = Column(Integer, default=50)  # Minimum priority score
    last_notified = Column(DateTime(timezone=True))
    notification_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    announcement = relationship("Announcement", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, name='{self.name}', tier='{self.tier}')>"


class PushToken(Base):
    """Push notification token model"""
    
    __tablename__ = "push_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Token information
    token = Column(String(500), nullable=False, unique=True)
    platform = Column(String(20), nullable=False)  # ios, android, web
    
    # Device information
    device_id = Column(String(100))
    app_version = Column(String(20))
    os_version = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="push_tokens")
    
    def __repr__(self):
        return f"<PushToken(id={self.id}, platform='{self.platform}')>"


class Notification(Base):
    """Notification history model"""
    
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id"), nullable=True)
    
    # Notification content
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSON)  # Additional data payload
    
    # Delivery information
    platform = Column(String(20))  # ios, android, web
    push_token_id = Column(UUID(as_uuid=True), ForeignKey("push_tokens.id"))
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    announcement = relationship("Announcement")
    push_token = relationship("PushToken")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, status='{self.status}')>"
