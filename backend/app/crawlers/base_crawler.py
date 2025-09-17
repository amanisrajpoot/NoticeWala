"""
Base crawler class for web scraping
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import structlog
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import settings

logger = structlog.get_logger()


class BaseCrawler(ABC):
    """Base class for all web crawlers"""
    
    def __init__(self, source_id: str, source_url: str):
        self.source_id = source_id
        self.source_url = source_url
        self.session = self._create_session()
        self.user_agents = [
            settings.SCRAPING_USER_AGENT,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def _create_session(self) -> Session:
        """Create a requests session with retry strategy"""
        session = Session()
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)
    
    def _make_request(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request with proper headers and error handling"""
        try:
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=settings.SCRAPING_TIMEOUT,
                **kwargs
            )
            
            response.raise_for_status()
            
            return {
                'url': url,
                'status_code': response.status_code,
                'content': response.content,
                'headers': dict(response.headers),
                'encoding': response.encoding
            }
            
        except Exception as e:
            logger.error(
                "Request failed",
                source_id=self.source_id,
                url=url,
                error=str(e)
            )
            return None
    
    @abstractmethod
    def crawl(self) -> List[Dict[str, Any]]:
        """Crawl the source and return raw data"""
        pass
    
    @abstractmethod
    def extract_announcements(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract announcements from raw data"""
        pass
    
    def process(self) -> List[Dict[str, Any]]:
        """Main processing method"""
        try:
            logger.info("Starting crawl", source_id=self.source_id)
            
            # Crawl the source
            raw_data = self.crawl()
            if not raw_data:
                logger.warning("No data crawled", source_id=self.source_id)
                return []
            
            # Extract announcements
            announcements = self.extract_announcements(raw_data)
            
            logger.info(
                "Crawl completed",
                source_id=self.source_id,
                announcements_count=len(announcements)
            )
            
            return announcements
            
        except Exception as e:
            logger.error(
                "Crawl failed",
                source_id=self.source_id,
                error=str(e)
            )
            return []
