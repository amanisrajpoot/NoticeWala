#!/usr/bin/env python3
"""
Test schema conversion
"""

from app.core.database import SessionLocal
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementResponse, AnnouncementListResponse

def test_schema_conversion():
    try:
        db = SessionLocal()
        
        # Get one announcement
        announcement = db.query(Announcement).first()
        print(f'Found announcement: {announcement.title}')
        
        # Try to convert to schema
        try:
            announcement_response = AnnouncementResponse.from_orm(announcement)
            print('✅ Schema conversion successful')
            print(f'Response title: {announcement_response.title}')
        except Exception as e:
            print(f'❌ Schema conversion failed: {e}')
            import traceback
            traceback.print_exc()
        
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema_conversion()
