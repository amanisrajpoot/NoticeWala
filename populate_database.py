#!/usr/bin/env python3
"""
Script to populate the database with sample data using crawlers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.crawlers.crawler_manager import crawler_manager
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.announcement import Source
import structlog

logger = structlog.get_logger()


def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


def populate_database():
    """Populate database with sample data"""
    try:
        logger.info("Starting database population")
        
        # Create tables first
        create_tables()
        
        # Run all crawlers
        result = crawler_manager.run_all_crawlers()
        
        if result.get("success"):
            logger.info("Database populated successfully", 
                       total_saved=result.get("total_announcements_saved", 0),
                       successful_crawls=result.get("successful_crawls", 0))
            
            # Print summary
            print("\n" + "="*50)
            print("🎉 DATABASE POPULATION COMPLETE!")
            print("="*50)
            print(f"✅ Total Crawlers Run: {result.get('total_crawlers', 0)}")
            print(f"✅ Successful Crawls: {result.get('successful_crawls', 0)}")
            print(f"✅ Failed Crawls: {result.get('failed_crawls', 0)}")
            print(f"✅ Total Announcements Saved: {result.get('total_announcements_saved', 0)}")
            print(f"⏱️  Total Duration: {result.get('duration_seconds', 0):.2f} seconds")
            print("="*50)
            
            # Print individual results
            for crawl_result in result.get("results", []):
                status = "✅" if crawl_result.get("success") else "❌"
                source = crawl_result.get("source", "Unknown")
                saved = crawl_result.get("saved_count", 0)
                print(f"{status} {source}: {saved} announcements saved")
            
            return True
        else:
            logger.error("Failed to populate database")
            return False
            
    except Exception as e:
        logger.error("Error populating database", error=str(e))
        return False


def check_database():
    """Check what's in the database"""
    try:
        db = SessionLocal()
        
        # Count sources
        source_count = db.query(Source).count()
        
        # Count announcements
        from backend.app.models.announcement import Announcement
        announcement_count = db.query(Announcement).count()
        
        # Get latest announcements
        latest_announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(5).all()
        
        print("\n" + "="*50)
        print("📊 DATABASE STATUS")
        print("="*50)
        print(f"📁 Sources: {source_count}")
        print(f"📄 Announcements: {announcement_count}")
        
        if latest_announcements:
            print("\n📋 Latest Announcements:")
            for i, announcement in enumerate(latest_announcements, 1):
                print(f"  {i}. {announcement.title}")
                print(f"     Source: {announcement.source.name if announcement.source else 'Unknown'}")
                print(f"     Published: {announcement.publish_date}")
                print()
        
        db.close()
        
    except Exception as e:
        logger.error("Error checking database", error=str(e))


if __name__ == "__main__":
    print("🚀 NoticeWala Database Population Script")
    print("="*50)
    
    # Populate database
    success = populate_database()
    
    if success:
        # Check what was created
        check_database()
        print("\n✅ Database population completed successfully!")
        print("🌐 You can now test the API endpoints:")
        print("   - GET /api/v1/announcements")
        print("   - GET /api/v1/crawlers/list")
        print("   - GET /api/v1/crawlers/stats")
    else:
        print("\n❌ Database population failed!")
        sys.exit(1)
