#!/usr/bin/env python3
"""
Test endpoint logic
"""

from app.core.database import SessionLocal
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementResponse, AnnouncementListResponse

def test_endpoint_logic():
    try:
        db = SessionLocal()
        
        # Build query (same as endpoint)
        query = db.query(Announcement).filter(Announcement.is_duplicate == False)
        
        # Get total count
        total = query.count()
        print(f'Total announcements: {total}')
        
        # Apply pagination
        announcements = query.offset(0).limit(20).all()
        print(f'Retrieved announcements: {len(announcements)}')
        
        # Convert to response objects
        announcement_responses = []
        for announcement in announcements:
            try:
                response = AnnouncementResponse.model_validate(announcement)
                announcement_responses.append(response)
            except Exception as e:
                print(f'Error converting announcement {announcement.title}: {e}')
        
        print(f'Successfully converted: {len(announcement_responses)}')
        
        # Create list response
        list_response = AnnouncementListResponse(
            items=announcement_responses,
            total=total,
            skip=0,
            limit=20
        )
        
        print(f'✅ List response created successfully with {len(list_response.items)} items')
        
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint_logic()
