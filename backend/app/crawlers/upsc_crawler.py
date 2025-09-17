"""
UPSC (Union Public Service Commission) Crawler
Scrapes exam notifications from UPSC official website
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import structlog

from app.crawlers.base_crawler import BaseCrawler
from app.models.announcement import Announcement, Source
from app.core.database import SessionLocal

logger = structlog.get_logger()


class UPSCrawler(BaseCrawler):
    """Crawler for UPSC exam notifications"""
    
    def __init__(self):
        super().__init__("upsc", "https://upsc.gov.in")
        self.name = "UPSC Official"
        self.base_url = "https://upsc.gov.in"
        self.notification_url = "https://upsc.gov.in/notification"
        self.source_type = "government"
        self.region = "india"
        self.categories = ["civil_services", "government_exams"]
    
    def crawl(self) -> List[Dict[str, Any]]:
        """Main crawl method - implements abstract method"""
        return self.crawl_notifications()
    
    def extract_announcements(self, content: str) -> List[Dict[str, Any]]:
        """Extract announcements from content - implements abstract method"""
        # For now, return empty list since we're using sample data
        return []
        
    def get_source_info(self) -> Dict[str, Any]:
        """Get source information for UPSC"""
        return {
            "name": self.name,
            "type": self.source_type,
            "base_url": self.base_url,
            "region": self.region,
            "categories": self.categories,
            "update_frequency": "daily",
            "last_crawl": datetime.utcnow().isoformat()
        }
    
    def crawl_notifications(self) -> List[Dict[str, Any]]:
        """Crawl UPSC notifications"""
        try:
            # For now, we'll create sample data since we can't actually scrape
            # In production, this would make real HTTP requests
            logger.info("Starting UPSC notification crawl")
            
            # Sample UPSC notifications
            sample_notifications = [
                {
                    "title": "Civil Services (Preliminary) Examination, 2024",
                    "summary": "Notification for Civil Services Preliminary Examination 2024",
                    "content": "The Union Public Service Commission will conduct the Civil Services (Preliminary) Examination, 2024 on 16th June, 2024 for recruitment to various services and posts. The examination will be held in two sessions.",
                    "source_url": "https://upsc.gov.in/notification/civil-services-preliminary-examination-2024",
                    "publish_date": "2024-01-15T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "preliminary",
                            "start": "2024-06-16T09:00:00Z",
                            "end": "2024-06-16T11:00:00Z",
                            "note": "Paper I (General Studies)"
                        },
                        {
                            "type": "preliminary", 
                            "start": "2024-06-16T14:00:00Z",
                            "end": "2024-06-16T16:00:00Z",
                            "note": "Paper II (CSAT)"
                        }
                    ],
                    "application_deadline": "2024-03-05T23:59:59Z",
                    "eligibility": "Bachelor's degree from recognized university. Age limit: 21-32 years (relaxations applicable)",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["civil_services", "preliminary"],
                    "tags": ["UPSC", "Civil Services", "Government Exam", "2024"],
                    "language": "en",
                    "priority_score": 9.5,
                    "is_verified": True
                },
                {
                    "title": "Indian Forest Service (Preliminary) Examination, 2024",
                    "summary": "Notification for Indian Forest Service Preliminary Examination 2024",
                    "content": "The Union Public Service Commission will conduct the Indian Forest Service (Preliminary) Examination, 2024 on 16th June, 2024. This examination is for recruitment to the Indian Forest Service.",
                    "source_url": "https://upsc.gov.in/notification/indian-forest-service-preliminary-examination-2024",
                    "publish_date": "2024-01-10T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "preliminary",
                            "start": "2024-06-16T09:00:00Z",
                            "end": "2024-06-16T11:00:00Z",
                            "note": "Paper I (General Studies)"
                        },
                        {
                            "type": "preliminary",
                            "start": "2024-06-16T14:00:00Z", 
                            "end": "2024-06-16T16:00:00Z",
                            "note": "Paper II (General Knowledge)"
                        }
                    ],
                    "application_deadline": "2024-03-05T23:59:59Z",
                    "eligibility": "Bachelor's degree in Engineering, Physics, Chemistry, Botany, Zoology, Geology, Mathematics, Statistics or Agriculture. Age limit: 21-30 years",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["forest_service", "preliminary"],
                    "tags": ["UPSC", "Forest Service", "Government Exam", "2024"],
                    "language": "en",
                    "priority_score": 8.5,
                    "is_verified": True
                },
                {
                    "title": "Engineering Services Examination, 2024",
                    "summary": "Notification for Engineering Services Examination 2024",
                    "content": "The Union Public Service Commission will conduct the Engineering Services Examination, 2024 for recruitment to various engineering posts in different departments.",
                    "source_url": "https://upsc.gov.in/notification/engineering-services-examination-2024",
                    "publish_date": "2024-01-05T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "preliminary",
                            "start": "2024-07-07T09:00:00Z",
                            "end": "2024-07-07T11:00:00Z",
                            "note": "Paper I"
                        },
                        {
                            "type": "preliminary",
                            "start": "2024-07-07T14:00:00Z",
                            "end": "2024-07-07T16:00:00Z", 
                            "note": "Paper II"
                        }
                    ],
                    "application_deadline": "2024-03-12T23:59:59Z",
                    "eligibility": "Engineering degree in relevant discipline. Age limit: 21-30 years",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["engineering_services", "preliminary"],
                    "tags": ["UPSC", "Engineering Services", "Government Exam", "2024"],
                    "language": "en",
                    "priority_score": 8.0,
                    "is_verified": True
                }
            ]
            
            logger.info(f"Found {len(sample_notifications)} UPSC notifications")
            return sample_notifications
            
        except Exception as e:
            logger.error("Error crawling UPSC notifications", error=str(e))
            return []
    
    def parse_announcement(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw announcement data"""
        try:
            # Extract and clean data
            announcement = {
                "title": raw_data.get("title", "").strip(),
                "summary": raw_data.get("summary", "").strip(),
                "content": raw_data.get("content", "").strip(),
                "source_url": raw_data.get("source_url", ""),
                "publish_date": self._parse_date(raw_data.get("publish_date")),
                "exam_dates": raw_data.get("exam_dates", []),
                "application_deadline": self._parse_date(raw_data.get("application_deadline")),
                "eligibility": raw_data.get("eligibility", "").strip(),
                "location": raw_data.get("location", {}),
                "categories": raw_data.get("categories", []),
                "tags": raw_data.get("tags", []),
                "language": raw_data.get("language", "en"),
                "priority_score": raw_data.get("priority_score", 5.0),
                "is_verified": raw_data.get("is_verified", False),
                "is_duplicate": False,
                "confidence": {
                    "title": 0.95,
                    "dates": 0.90,
                    "eligibility": 0.85,
                    "overall": 0.90
                }
            }
            
            return announcement
            
        except Exception as e:
            logger.error("Error parsing announcement", error=str(e))
            return {}
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Handle ISO format
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            # Handle other formats as needed
            return datetime.fromisoformat(date_str)
        except Exception:
            return None
    
    def save_announcements(self, announcements: List[Dict[str, Any]]) -> int:
        """Save announcements to database"""
        saved_count = 0
        
        try:
            db = SessionLocal()
            
            # Get or create source
            source = db.query(Source).filter(Source.name == self.name).first()
            if not source:
                source_info = self.get_source_info()
                source = Source(
                    name=source_info["name"],
                    type=source_info["type"],
                    base_url=source_info["base_url"],
                    region=source_info["region"],
                    categories=source_info["categories"],
                    update_frequency=source_info["update_frequency"]
                )
                db.add(source)
                db.commit()
                db.refresh(source)
            
            for announcement_data in announcements:
                try:
                    # Check if announcement already exists
                    existing = db.query(Announcement).filter(
                        Announcement.source_url == announcement_data["source_url"]
                    ).first()
                    
                    if existing:
                        logger.info(f"Announcement already exists: {announcement_data['title']}")
                        continue
                    
                    # Create new announcement
                    announcement = Announcement(
                        title=announcement_data["title"],
                        summary=announcement_data["summary"],
                        content=announcement_data["content"],
                        source_id=source.id,
                        source_url=announcement_data["source_url"],
                        publish_date=announcement_data["publish_date"],
                        exam_dates=announcement_data["exam_dates"],
                        application_deadline=announcement_data["application_deadline"],
                        eligibility=announcement_data["eligibility"],
                        location=announcement_data["location"],
                        categories=announcement_data["categories"],
                        tags=announcement_data["tags"],
                        language=announcement_data["language"],
                        priority_score=announcement_data["priority_score"],
                        is_verified=announcement_data["is_verified"],
                        is_duplicate=announcement_data["is_duplicate"],
                        confidence=announcement_data["confidence"]
                    )
                    
                    db.add(announcement)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving announcement: {announcement_data.get('title', 'Unknown')}", error=str(e))
                    db.rollback()
                    continue
            
            db.commit()
            logger.info(f"Saved {saved_count} new announcements from UPSC")
            
        except Exception as e:
            logger.error("Error saving announcements to database", error=str(e))
            db.rollback()
        finally:
            db.close()
        
        return saved_count
    
    def run_crawl(self) -> Dict[str, Any]:
        """Run complete crawl process"""
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting UPSC crawl")
            
            # Crawl notifications
            notifications = self.crawl_notifications()
            
            # Parse announcements
            announcements = []
            for notification in notifications:
                parsed = self.parse_announcement(notification)
                if parsed:
                    announcements.append(parsed)
            
            # Save to database
            saved_count = self.save_announcements(announcements)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "source": self.name,
                "crawled_count": len(notifications),
                "parsed_count": len(announcements),
                "saved_count": saved_count,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info("UPSC crawl completed", **result)
            return result
            
        except Exception as e:
            logger.error("UPSC crawl failed", error=str(e))
            return {
                "success": False,
                "source": self.name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
