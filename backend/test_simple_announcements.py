#!/usr/bin/env python3
"""
Test simple announcements query
"""

from app.core.database import SessionLocal
from app.models.announcement import Announcement, Source
from app.schemas.announcement import AnnouncementResponse, AnnouncementListResponse

def test_simple_query():
    try:
        db = SessionLocal()
        
        # Simple query
        announcements = db.query(Announcement).limit(5).all()
        print(f'Found {len(announcements)} announcements')
        
        for announcement in announcements:
            print(f'- {announcement.title}')
            print(f'  Source: {announcement.source.name if announcement.source else "None"}')
            print(f'  Created: {announcement.created_at}')
        
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_query()
