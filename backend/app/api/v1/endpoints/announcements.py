"""
Announcements API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.announcement import Announcement, Source
from app.models.user import User
from app.schemas.announcement import AnnouncementResponse, AnnouncementListResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=AnnouncementListResponse)
async def get_announcements(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Get list of announcements with optional filtering and search"""
    
    try:
        # Build query
        query = db.query(Announcement).filter(Announcement.is_duplicate == False)
        
        # Apply filters
        if category:
            query = query.filter(Announcement.categories.contains([category]))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Announcement.title.ilike(search_term) |
                Announcement.summary.ilike(search_term) |
                Announcement.content.ilike(search_term)
            )
        
        # Apply sorting
        sort_column = getattr(Announcement, sort_by, Announcement.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        announcements = query.offset(skip).limit(limit).all()
        
        logger.info(
            "Announcements retrieved",
            count=len(announcements),
            total=total,
            filters={"category": category, "search": search}
        )
        
        return AnnouncementListResponse(
            items=announcements,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error("Failed to retrieve announcements", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve announcements"
        )


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific announcement by ID"""
    
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        logger.info("Announcement retrieved", announcement_id=announcement_id)
        return announcement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve announcement",
            announcement_id=announcement_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve announcement"
        )


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of available categories"""
    
    try:
        # Get unique categories from announcements
        result = db.query(Announcement.categories).filter(
            Announcement.categories.isnot(None)
        ).all()
        
        categories = set()
        for row in result:
            if row.categories:
                categories.update(row.categories)
        
        category_list = sorted(list(categories))
        
        logger.info("Categories retrieved", count=len(category_list))
        return {"categories": category_list}
        
    except Exception as e:
        logger.error("Failed to retrieve categories", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/sources/list")
async def get_sources(db: Session = Depends(get_db)):
    """Get list of available sources"""
    
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        source_list = [
            {
                "id": str(source.id),
                "name": source.name,
                "type": source.type,
                "category": source.category,
                "region": source.region
            }
            for source in sources
        ]
        
        logger.info("Sources retrieved", count=len(source_list))
        return {"sources": source_list}
        
    except Exception as e:
        logger.error("Failed to retrieve sources", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sources"
        )
