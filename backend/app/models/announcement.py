"""
Announcement database model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Announcement(Base):
    """Announcement model for storing exam notifications"""
    
    __tablename__ = "announcements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text)
    content = Column(Text)
    
    # Source information
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    source_url = Column(String(1000), nullable=False)
    publish_date = Column(DateTime(timezone=True))
    
    # Exam specific fields
    exam_dates = Column(JSON)  # List of exam date objects
    application_deadline = Column(DateTime(timezone=True))
    eligibility = Column(Text)
    location = Column(JSON)  # Location object with country, state, city
    
    # Metadata
    categories = Column(JSON)  # List of categories
    tags = Column(JSON)  # List of tags
    language = Column(String(10), default="en")
    priority_score = Column(Float, default=0.5)
    
    # Quality and confidence
    confidence = Column(JSON)  # Confidence scores for extracted fields
    is_verified = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source = relationship("Source", back_populates="announcements")
    attachments = relationship("Attachment", back_populates="announcement", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="announcement")
    
    def __repr__(self):
        return f"<Announcement(id={self.id}, title='{self.title[:50]}...')>"


class Source(Base):
    """Source model for tracking information sources"""
    
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    base_url = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)  # rss, website, api, etc.
    
    # Crawling configuration
    update_frequency = Column(String(50), default="daily")  # daily, weekly, etc.
    last_crawled = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Metadata
    description = Column(Text)
    categories = Column(JSON)  # List of categories
    region = Column(String(100))
    
    # Quality metrics
    success_rate = Column(Float, default=1.0)
    avg_response_time = Column(Float)
    total_crawls = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    announcements = relationship("Announcement", back_populates="source")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}')>"


class Attachment(Base):
    """Attachment model for storing file attachments"""
    
    __tablename__ = "attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("announcements.id"), nullable=False)
    
    # File information
    filename = Column(String(500), nullable=False)
    file_url = Column(String(1000), nullable=False)
    file_type = Column(String(50))  # pdf, image, doc, etc.
    file_size = Column(Integer)
    checksum = Column(String(64))  # SHA256 hash
    
    # Metadata
    title = Column(String(500))
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    announcement = relationship("Announcement", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}')>"
