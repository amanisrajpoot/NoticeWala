"""
AI-Enhanced Crawler that uses OpenAI for content processing
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from app.crawlers.base_crawler import BaseCrawler
from app.services.ai_service import ai_service
from app.models.announcement import Announcement, Source, Attachment
from app.core.database import SessionLocal
from app.core.config import settings

logger = structlog.get_logger()


class AIEnhancedCrawler(BaseCrawler):
    """AI-enhanced crawler that uses OpenAI for content processing"""
    
    def __init__(self, source_id: str, source_url: str):
        super().__init__(source_id, source_url)
        self.ai_service = ai_service
        self.name = "AI Enhanced Crawler"
        self.source_type = "ai_enhanced"
        self.region = "india"
        self.categories = ["ai_processed", "enhanced_extraction"]
        self.last_crawl_time = None
    
    def crawl(self) -> List[Dict[str, Any]]:
        """Main crawl method - implements abstract method"""
        return self.crawl_with_ai_processing()
    
    def extract_announcements(self, content: str) -> List[Dict[str, Any]]:
        """Extract announcements from content - implements abstract method"""
        return []
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get source information for AI enhanced crawler"""
        return {
            "name": self.name,
            "type": self.source_type,
            "base_url": self.source_url,
            "region": self.region,
            "categories": self.categories,
            "update_frequency": "daily",
            "last_crawl": self.last_crawl_time.isoformat() if self.last_crawl_time else None
        }
    
    async def crawl_with_ai_processing(self) -> List[Dict[str, Any]]:
        """Crawl with AI-enhanced processing"""
        
        logger.info("Starting AI-enhanced crawl")
        
        # Get existing announcements from database for AI processing
        db = SessionLocal()
        try:
            # Get recent announcements that haven't been AI processed
            announcements = db.query(Announcement).filter(
                Announcement.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).limit(50).all()
            
            enhanced_announcements = []
            
            for announcement in announcements:
                try:
                    # Process with AI
                    enhanced_data = await self.ai_service.extract_structured_data(
                        content=announcement.content or announcement.summary or "",
                        title=announcement.title
                    )
                    
                    # Create enhanced announcement
                    enhanced_announcement = {
                        "id": str(announcement.id),
                        "title": announcement.title,
                        "summary": announcement.summary or self.ai_service.generate_summary(
                            announcement.content or announcement.title, 150
                        ),
                        "content": announcement.content,
                        "source_url": announcement.source_url,
                        "publish_date": announcement.publish_date.isoformat() if announcement.publish_date else None,
                        "source": {
                            "id": str(announcement.source.id),
                            "name": announcement.source.name,
                            "type": announcement.source.type
                        },
                        "created_at": announcement.created_at.isoformat(),
                        "updated_at": announcement.updated_at.isoformat() if announcement.updated_at else None,
                        **enhanced_data  # Merge AI-extracted data
                    }
                    
                    enhanced_announcements.append(enhanced_announcement)
                    
                    # Update original announcement with AI data
                    self._update_announcement_with_ai_data(announcement, enhanced_data)
                    
                except Exception as e:
                    logger.error(f"Failed to process announcement {announcement.id} with AI: {e}")
                    continue
            
            db.commit()
            logger.info(f"AI-enhanced {len(enhanced_announcements)} announcements")
            
            return enhanced_announcements
            
        except Exception as e:
            logger.error(f"AI-enhanced crawl failed: {e}")
            db.rollback()
            return []
        finally:
            db.close()
    
    def _update_announcement_with_ai_data(self, announcement: Announcement, ai_data: Dict[str, Any]):
        """Update announcement with AI-extracted data"""
        
        try:
            # Update exam dates
            if ai_data.get("exam_dates"):
                announcement.exam_dates = ai_data["exam_dates"]
            
            # Update application deadline
            if ai_data.get("application_deadline"):
                from dateparser import parse as date_parse
                deadline = date_parse(ai_data["application_deadline"])
                if deadline:
                    announcement.application_deadline = deadline
            
            # Update eligibility
            if ai_data.get("eligibility"):
                announcement.eligibility = ai_data["eligibility"]
            
            # Update location
            if ai_data.get("location"):
                announcement.location = ai_data["location"]
            
            # Update categories (merge with existing)
            existing_categories = announcement.categories or []
            new_categories = ai_data.get("categories", [])
            all_categories = list(set(existing_categories + new_categories))
            announcement.categories = all_categories[:10]  # Limit to 10
            
            # Update tags (merge with existing)
            existing_tags = announcement.tags or []
            new_tags = ai_data.get("tags", [])
            all_tags = list(set(existing_tags + new_tags))
            announcement.tags = all_tags[:15]  # Limit to 15
            
            # Update priority score
            if ai_data.get("priority_score"):
                announcement.priority_score = ai_data["priority_score"]
            
            # Update confidence
            if ai_data.get("confidence"):
                announcement.confidence = ai_data["confidence"]
            
            # Update summary if AI generated a better one
            if ai_data.get("summary") and len(ai_data["summary"]) > len(announcement.summary or ""):
                announcement.summary = ai_data["summary"]
            
            # Mark as AI processed
            if not announcement.confidence:
                announcement.confidence = {}
            announcement.confidence["ai_processed"] = True
            announcement.confidence["ai_processing_date"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Failed to update announcement with AI data: {e}")
    
    def run_crawl(self) -> Dict[str, Any]:
        """Run complete AI-enhanced crawl process"""
        
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting AI-enhanced crawl")
            
            # Run AI processing
            enhanced_announcements = asyncio.run(self.crawl_with_ai_processing())
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            self.last_crawl_time = end_time
            
            result = {
                "success": True,
                "source": self.name,
                "processed_count": len(enhanced_announcements),
                "duration_seconds": duration,
                "timestamp": end_time.isoformat(),
                "ai_processing_enabled": settings.AI_PROCESSING_ENABLED
            }
            
            logger.info("AI-enhanced crawl completed", **result)
            return result
            
        except Exception as e:
            logger.error("AI-enhanced crawl failed", error=str(e))
            return {
                "success": False,
                "source": self.name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def detect_duplicates(self) -> Dict[str, Any]:
        """Detect and handle duplicate announcements using AI"""
        
        db = SessionLocal()
        try:
            # Get recent announcements
            announcements = db.query(Announcement).filter(
                Announcement.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).limit(100).all()
            
            # Convert to list of dictionaries for processing
            announcement_data = []
            for announcement in announcements:
                announcement_data.append({
                    "id": str(announcement.id),
                    "title": announcement.title,
                    "summary": announcement.summary or "",
                    "content": announcement.content or ""
                })
            
            # Detect duplicates using AI
            duplicates = self.ai_service.detect_duplicates(announcement_data, threshold=0.85)
            
            # Mark duplicates
            duplicate_count = 0
            for i, j, similarity in duplicates:
                if i < len(announcements) and j < len(announcements):
                    # Mark the newer one as duplicate
                    if announcements[i].created_at < announcements[j].created_at:
                        announcements[j].is_duplicate = True
                        announcements[j].confidence = announcements[j].confidence or {}
                        announcements[j].confidence["duplicate_similarity"] = similarity
                        announcements[j].confidence["duplicate_of"] = str(announcements[i].id)
                    else:
                        announcements[i].is_duplicate = True
                        announcements[i].confidence = announcements[i].confidence or {}
                        announcements[i].confidence["duplicate_similarity"] = similarity
                        announcements[i].confidence["duplicate_of"] = str(announcements[j].id)
                    
                    duplicate_count += 1
            
            db.commit()
            
            return {
                "success": True,
                "duplicates_found": len(duplicates),
                "duplicates_marked": duplicate_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights from crawled data using AI"""
        
        db = SessionLocal()
        try:
            # Get recent announcements
            announcements = db.query(Announcement).filter(
                Announcement.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).all()
            
            # Analyze categories
            category_counts = {}
            source_counts = {}
            priority_scores = []
            
            for announcement in announcements:
                # Count categories
                if announcement.categories:
                    for category in announcement.categories:
                        category_counts[category] = category_counts.get(category, 0) + 1
                
                # Count sources
                source_name = announcement.source.name
                source_counts[source_name] = source_counts.get(source_name, 0) + 1
                
                # Collect priority scores
                if announcement.priority_score:
                    priority_scores.append(announcement.priority_score)
            
            # Generate insights
            insights = {
                "total_announcements": len(announcements),
                "top_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "top_sources": sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "average_priority_score": sum(priority_scores) / len(priority_scores) if priority_scores else 0,
                "high_priority_count": len([score for score in priority_scores if score >= 8.0]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Generated insights", **insights)
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
