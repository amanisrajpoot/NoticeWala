"""
Real IBPS Crawler - Actually scrapes IBPS website for live banking exam notifications
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import structlog
from bs4 import BeautifulSoup
import requests
from dateparser import parse as parse_date

from app.crawlers.base_crawler import BaseCrawler
from app.models.announcement import Announcement, Source
from app.core.database import SessionLocal

logger = structlog.get_logger()


class RealIBPSCrawler(BaseCrawler):
    """Real crawler for IBPS banking exam notifications"""
    
    def __init__(self):
        super().__init__("ibps", "https://www.ibps.in")
        self.name = "IBPS Official"
        self.base_url = "https://www.ibps.in"
        self.notification_url = "https://www.ibps.in/career/"
        self.source_type = "government"
        self.region = "india"
        self.categories = ["banking_exams", "government_exams"]
        
        # Real IBPS URLs to scrape
        self.scrape_urls = [
            "https://www.ibps.in/career/",
            "https://www.ibps.in/current-openings/",
            "https://www.ibps.in/notifications/",
            "https://www.ibps.in/upcoming-exams/"
        ]
    
    def crawl(self) -> List[Dict[str, Any]]:
        """Main crawl method - implements abstract method"""
        return self.crawl_real_notifications()
    
    def extract_announcements(self, content: str) -> List[Dict[str, Any]]:
        """Extract announcements from content - implements abstract method"""
        announcements = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for notification links and content
            notification_links = soup.find_all('a', href=re.compile(r'/career|/notification|/exam|/recruitment|/advertisement'))
            
            for link in notification_links:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if not title or len(title) < 10:
                        continue
                    
                    # Skip if it's not a notification link
                    if not any(keyword in title.lower() for keyword in ['notification', 'exam', 'recruitment', 'examination', 'advertisement', 'notice', 'po', 'clerk', 'so', 'rrb']):
                        continue
                    
                    full_url = urljoin(self.base_url, href)
                    
                    # Get detailed content
                    announcement_data = self._scrape_notification_details(full_url, title)
                    if announcement_data:
                        announcements.append(announcement_data)
                        
                except Exception as e:
                    logger.warning(f"Error processing notification link: {e}")
                    continue
            
            # Also look for notification tables or lists
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            title_cell = cells[0]
                            link = title_cell.find('a')
                            if link:
                                title = link.get_text(strip=True)
                                href = link.get('href', '')
                                full_url = urljoin(self.base_url, href)
                                
                                if len(title) > 10 and any(keyword in title.lower() for keyword in ['notification', 'exam', 'recruitment', 'advertisement', 'po', 'clerk', 'so']):
                                    announcement_data = self._scrape_notification_details(full_url, title)
                                    if announcement_data:
                                        announcements.append(announcement_data)
                        except Exception as e:
                            logger.warning(f"Error processing table row: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Error extracting announcements from content: {e}")
        
        return announcements
    
    def _scrape_notification_details(self, url: str, title: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information from a notification page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content_divs = soup.find_all(['div', 'p'], class_=re.compile(r'content|notification|details', re.I))
            content = ""
            for div in content_divs:
                content += div.get_text(strip=True) + "\n"
            
            if not content:
                # Fallback: get all text content
                content = soup.get_text(strip=True)
            
            # Extract dates
            publish_date = self._extract_date(soup, response.text)
            application_deadline = self._extract_deadline(soup, response.text)
            exam_dates = self._extract_exam_dates(soup, response.text)
            
            # Extract eligibility
            eligibility = self._extract_eligibility(soup, response.text)
            
            # Determine categories based on title and content
            categories = self._determine_categories(title, content)
            
            # Calculate priority score
            priority_score = self._calculate_priority_score(title, content, categories)
            
            return {
                "title": title,
                "summary": content[:200] + "..." if len(content) > 200 else content,
                "content": content,
                "source_url": url,
                "publish_date": publish_date,
                "exam_dates": exam_dates,
                "application_deadline": application_deadline,
                "eligibility": eligibility,
                "location": {"country": "India", "state": "All States", "city": "Multiple Centers"},
                "categories": categories,
                "tags": self._generate_tags(title, content),
                "language": "en",
                "priority_score": priority_score,
                "is_verified": True,
                "is_duplicate": False,
                "confidence": {
                    "title": 0.95,
                    "dates": 0.80,
                    "eligibility": 0.70,
                    "overall": 0.82
                }
            }
            
        except Exception as e:
            logger.warning(f"Error scraping notification details from {url}: {e}")
            return None
    
    def _extract_date(self, soup: BeautifulSoup, text: str) -> Optional[datetime]:
        """Extract publication date"""
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[0]
                    parsed_date = parse_date(date_str)
                    if parsed_date:
                        return parsed_date
                except:
                    continue
        
        return None
    
    def _extract_deadline(self, soup: BeautifulSoup, text: str) -> Optional[datetime]:
        """Extract application deadline"""
        deadline_patterns = [
            r'last date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'closing date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'deadline[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'application deadline[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
        ]
        
        for pattern in deadline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[0]
                    parsed_date = parse_date(date_str)
                    if parsed_date:
                        return parsed_date
                except:
                    continue
        
        return None
    
    def _extract_exam_dates(self, soup: BeautifulSoup, text: str) -> List[Dict[str, Any]]:
        """Extract exam dates"""
        exam_dates = []
        
        date_patterns = [
            r'exam date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'examination[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'conducted on[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'online exam[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    parsed_date = parse_date(match)
                    if parsed_date:
                        exam_dates.append({
                            "type": "examination",
                            "start": parsed_date.isoformat(),
                            "end": (parsed_date + timedelta(hours=3)).isoformat(),
                            "note": "Examination Date"
                        })
                except:
                    continue
        
        return exam_dates
    
    def _extract_eligibility(self, soup: BeautifulSoup, text: str) -> str:
        """Extract eligibility criteria"""
        eligibility_keywords = ['eligibility', 'qualification', 'educational qualification']
        
        for keyword in eligibility_keywords:
            pattern = rf'{keyword}[:\s]+([^.]+\.)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _determine_categories(self, title: str, content: str) -> List[str]:
        """Determine categories based on title and content"""
        categories = []
        text = (title + " " + content).lower()
        
        if any(word in text for word in ['po', 'probationary officer']):
            categories.append('po')
        if any(word in text for word in ['clerk', 'office assistant']):
            categories.append('clerk')
        if any(word in text for word in ['so', 'specialist officer']):
            categories.append('so')
        if any(word in text for word in ['rrb', 'regional rural bank']):
            categories.append('rrb')
        if any(word in text for word in ['mains']):
            categories.append('mains')
        if any(word in text for word in ['prelims', 'preliminary']):
            categories.append('prelims')
        if any(word in text for word in ['interview']):
            categories.append('interview')
        
        if not categories:
            categories = ['banking_exams']
        
        return categories
    
    def _calculate_priority_score(self, title: str, content: str, categories: List[str]) -> float:
        """Calculate priority score for the announcement"""
        score = 5.0  # Base score
        
        # Higher priority for important banking exams
        if 'po' in categories:
            score += 3.0
        if 'clerk' in categories:
            score += 2.5
        if 'so' in categories:
            score += 2.0
        if 'rrb' in categories:
            score += 1.5
        
        # Higher priority for recent announcements
        if '2024' in title or '2025' in title:
            score += 1.0
        
        # Higher priority for active recruitment
        if any(word in content.lower() for word in ['recruitment', 'vacancy', 'post']):
            score += 1.5
        
        return min(score, 10.0)  # Cap at 10
    
    def _generate_tags(self, title: str, content: str) -> List[str]:
        """Generate tags for the announcement"""
        tags = ['IBPS']
        
        if '2024' in title:
            tags.append('2024')
        if '2025' in title:
            tags.append('2025')
        
        if 'po' in title.lower():
            tags.append('PO')
        if 'clerk' in title.lower():
            tags.append('Clerk')
        if 'so' in title.lower():
            tags.append('SO')
        if 'rrb' in title.lower():
            tags.append('RRB')
        
        return tags
    
    def crawl_real_notifications(self) -> List[Dict[str, Any]]:
        """Crawl real IBPS notifications"""
        all_announcements = []
        
        try:
            logger.info("Starting real IBPS notification crawl")
            
            for url in self.scrape_urls:
                try:
                    logger.info(f"Scraping URL: {url}")
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    
                    announcements = self.extract_announcements(response.text)
                    all_announcements.extend(announcements)
                    
                    logger.info(f"Found {len(announcements)} announcements from {url}")
                    
                    # Be respectful - add delay between requests
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
            
            logger.info(f"Total announcements found: {len(all_announcements)}")
            return all_announcements
            
        except Exception as e:
            logger.error(f"Error in real IBPS crawl: {e}")
            return []
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get source information for IBPS"""
        return {
            "name": self.name,
            "type": self.source_type,
            "base_url": self.base_url,
            "region": self.region,
            "categories": self.categories,
            "update_frequency": "daily",
            "last_crawl": datetime.utcnow().isoformat()
        }
    
    def run_crawl(self) -> Dict[str, Any]:
        """Run complete crawl process"""
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting real IBPS crawl")
            
            # Crawl notifications
            notifications = self.crawl_real_notifications()
            
            # Save to database
            saved_count = self.save_announcements(notifications)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "source": self.name,
                "crawled_count": len(notifications),
                "saved_count": saved_count,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info("Real IBPS crawl completed", **result)
            return result
            
        except Exception as e:
            logger.error("Real IBPS crawl failed", error=str(e))
            return {
                "success": False,
                "source": self.name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
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
            logger.info(f"Saved {saved_count} new announcements from real IBPS crawl")
            
        except Exception as e:
            logger.error("Error saving announcements to database", error=str(e))
            db.rollback()
        finally:
            db.close()
        
        return saved_count
