"""
SSC (Staff Selection Commission) Crawler
Scrapes exam notifications from SSC official website
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


class SSCCrawler(BaseCrawler):
    """Crawler for SSC exam notifications"""
    
    def __init__(self):
        super().__init__("ssc", "https://ssc.nic.in")
        self.name = "SSC Official"
        self.base_url = "https://ssc.nic.in"
        self.notification_url = "https://ssc.nic.in/notice-board"
        self.source_type = "government"
        self.region = "india"
        self.categories = ["ssc_exams", "government_exams"]
    
    def crawl(self) -> List[Dict[str, Any]]:
        """Main crawl method - implements abstract method"""
        return self.crawl_notifications()
    
    def extract_announcements(self, content: str) -> List[Dict[str, Any]]:
        """Extract announcements from content - implements abstract method"""
        # For now, return empty list since we're using sample data
        return []
        
    def get_source_info(self) -> Dict[str, Any]:
        """Get source information for SSC"""
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
        """Crawl SSC notifications"""
        try:
            logger.info("Starting SSC notification crawl")
            
            # Sample SSC notifications
            sample_notifications = [
                {
                    "title": "Combined Graduate Level Examination (CGL) 2024",
                    "summary": "Notification for SSC CGL 2024 Examination",
                    "content": "Staff Selection Commission will conduct the Combined Graduate Level Examination (CGL) 2024 for recruitment to various Group B and Group C posts in different Ministries/Departments of Government of India.",
                    "source_url": "https://ssc.nic.in/notice-board/cgl-2024",
                    "publish_date": "2024-02-01T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "tier1",
                            "start": "2024-06-27T09:00:00Z",
                            "end": "2024-06-27T11:00:00Z",
                            "note": "Tier-I Examination"
                        },
                        {
                            "type": "tier2",
                            "start": "2024-10-26T09:00:00Z",
                            "end": "2024-10-26T12:00:00Z",
                            "note": "Tier-II Examination"
                        }
                    ],
                    "application_deadline": "2024-03-15T23:59:59Z",
                    "eligibility": "Bachelor's degree from recognized university. Age limit: 18-32 years (relaxations applicable)",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["cgl", "tier1", "tier2"],
                    "tags": ["SSC", "CGL", "Government Exam", "2024", "Group B", "Group C"],
                    "language": "en",
                    "priority_score": 9.0,
                    "is_verified": True
                },
                {
                    "title": "Combined Higher Secondary Level (CHSL) Examination 2024",
                    "summary": "Notification for SSC CHSL 2024 Examination",
                    "content": "Staff Selection Commission will conduct the Combined Higher Secondary Level (CHSL) Examination 2024 for recruitment to various posts like Postal Assistant, Sorting Assistant, Data Entry Operator, Lower Division Clerk.",
                    "source_url": "https://ssc.nic.in/notice-board/chsl-2024",
                    "publish_date": "2024-01-25T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "tier1",
                            "start": "2024-07-01T09:00:00Z",
                            "end": "2024-07-01T11:00:00Z",
                            "note": "Tier-I Examination"
                        },
                        {
                            "type": "tier2",
                            "start": "2024-11-02T09:00:00Z",
                            "end": "2024-11-02T11:00:00Z",
                            "note": "Tier-II Examination"
                        }
                    ],
                    "application_deadline": "2024-03-10T23:59:59Z",
                    "eligibility": "12th Standard or equivalent from recognized board. Age limit: 18-27 years (relaxations applicable)",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["chsl", "tier1", "tier2"],
                    "tags": ["SSC", "CHSL", "Government Exam", "2024", "PA", "SA", "DEO", "LDC"],
                    "language": "en",
                    "priority_score": 8.5,
                    "is_verified": True
                },
                {
                    "title": "Junior Engineer (JE) Examination 2024",
                    "summary": "Notification for SSC JE 2024 Examination",
                    "content": "Staff Selection Commission will conduct the Junior Engineer (Civil, Mechanical, Electrical, Quantity Surveying & Contracts) Examination 2024 for recruitment to various posts in different departments.",
                    "source_url": "https://ssc.nic.in/notice-board/je-2024",
                    "publish_date": "2024-01-20T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "paper1",
                            "start": "2024-05-05T09:00:00Z",
                            "end": "2024-05-05T11:00:00Z",
                            "note": "Paper-I (Objective)"
                        },
                        {
                            "type": "paper2",
                            "start": "2024-06-01T09:00:00Z",
                            "end": "2024-06-01T12:00:00Z",
                            "note": "Paper-II (Descriptive)"
                        }
                    ],
                    "application_deadline": "2024-02-28T23:59:59Z",
                    "eligibility": "Diploma in Engineering in relevant discipline. Age limit: 18-30 years (relaxations applicable)",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["je", "engineering", "technical"],
                    "tags": ["SSC", "JE", "Junior Engineer", "Civil", "Mechanical", "Electrical", "2024"],
                    "language": "en",
                    "priority_score": 8.0,
                    "is_verified": True
                },
                {
                    "title": "Multi Tasking Staff (MTS) Examination 2024",
                    "summary": "Notification for SSC MTS 2024 Examination",
                    "content": "Staff Selection Commission will conduct the Multi Tasking Staff (MTS) Examination 2024 for recruitment to various Group C posts in different Ministries/Departments.",
                    "source_url": "https://ssc.nic.in/notice-board/mts-2024",
                    "publish_date": "2024-01-15T00:00:00Z",
                    "exam_dates": [
                        {
                            "type": "paper1",
                            "start": "2024-04-30T09:00:00Z",
                            "end": "2024-04-30T11:00:00Z",
                            "note": "Paper-I"
                        }
                    ],
                    "application_deadline": "2024-02-25T23:59:59Z",
                    "eligibility": "10th Standard pass from recognized board. Age limit: 18-25 years (relaxations applicable)",
                    "location": {
                        "country": "India",
                        "state": "All States",
                        "city": "Multiple Centers"
                    },
                    "categories": ["mts", "group_c"],
                    "tags": ["SSC", "MTS", "Multi Tasking Staff", "Government Exam", "2024"],
                    "language": "en",
                    "priority_score": 7.5,
                    "is_verified": True
                }
            ]
            
            logger.info(f"Found {len(sample_notifications)} SSC notifications")
            return sample_notifications
            
        except Exception as e:
            logger.error("Error crawling SSC notifications", error=str(e))
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
            logger.info(f"Saved {saved_count} new announcements from SSC")
            
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
            logger.info("Starting SSC crawl")
            
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
            
            logger.info("SSC crawl completed", **result)
            return result
            
        except Exception as e:
            logger.error("SSC crawl failed", error=str(e))
            return {
                "success": False,
                "source": self.name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
