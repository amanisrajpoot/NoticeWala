#!/usr/bin/env python3
"""
Initialize database with all models
"""

from app.core.database import Base, engine
from app.models.announcement import Announcement, Source, Attachment
from app.models.user import User, PushToken, Subscription, Notification

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Check what tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Created {len(tables)} tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_tables()
