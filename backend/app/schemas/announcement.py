"""
Announcement schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ExamDate(BaseModel):
    """Schema for exam date information"""
    type: str  # exam_date, application_deadline, result_date, etc.
    start: datetime
    end: Optional[datetime] = None
    note: Optional[str] = None


class Location(BaseModel):
    """Schema for location information"""
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class SourceResponse(BaseModel):
    """Schema for source information"""
    id: str
    name: str
    type: str
    category: Optional[str] = None
    region: Optional[str] = None
    
    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    """Schema for attachment information"""
    id: str
    filename: str
    file_url: HttpUrl
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    title: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnnouncementResponse(BaseModel):
    """Schema for announcement response"""
    id: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: SourceResponse
    source_url: HttpUrl
    publish_date: Optional[datetime] = None
    exam_dates: Optional[List[ExamDate]] = None
    application_deadline: Optional[datetime] = None
    eligibility: Optional[str] = None
    location: Optional[Location] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    language: str = "en"
    priority_score: float = 0.5
    confidence: Optional[Dict[str, float]] = None
    is_verified: bool = False
    attachments: Optional[List[AttachmentResponse]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnnouncementListResponse(BaseModel):
    """Schema for announcement list response"""
    items: List[AnnouncementResponse]
    total: int
    skip: int
    limit: int


class AnnouncementSearchRequest(BaseModel):
    """Schema for announcement search request"""
    query: Optional[str] = None
    categories: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sources: Optional[List[str]] = None
    min_priority: Optional[float] = None
    verified_only: bool = False
    skip: int = 0
    limit: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"
