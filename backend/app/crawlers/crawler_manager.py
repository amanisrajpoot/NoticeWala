"""
Crawler Manager for NoticeWala
Manages and executes all crawlers
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from app.crawlers.improved_upsc_crawler import ImprovedUPSCrawler
from app.crawlers.improved_ssc_crawler import ImprovedSSCCrawler
from app.crawlers.improved_ibps_crawler import ImprovedIBPSCrawler
from app.crawlers.nta_crawler import NTACrawler
from app.crawlers.additional_sources_crawler import AdditionalSourcesCrawler

logger = structlog.get_logger()


class CrawlerManager:
    """Manager for all crawlers"""
    
    def __init__(self):
        self.crawlers = [
            ImprovedUPSCrawler(),
            ImprovedSSCCrawler(),
            ImprovedIBPSCrawler(),
            NTACrawler(),
            AdditionalSourcesCrawler()
        ]
        self.results = []
    
    def get_crawler_by_name(self, name: str):
        """Get crawler by name"""
        for crawler in self.crawlers:
            if crawler.name.lower() == name.lower():
                return crawler
        return None
    
    def list_crawlers(self) -> List[Dict[str, Any]]:
        """List all available crawlers"""
        return [
            {
                "name": crawler.name,
                "type": crawler.source_type,
                "base_url": crawler.base_url,
                "region": crawler.region,
                "categories": crawler.categories
            }
            for crawler in self.crawlers
        ]
    
    def run_single_crawler(self, crawler_name: str) -> Dict[str, Any]:
        """Run a single crawler"""
        crawler = self.get_crawler_by_name(crawler_name)
        if not crawler:
            return {
                "success": False,
                "error": f"Crawler '{crawler_name}' not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            logger.info(f"Running crawler: {crawler_name}")
            result = crawler.run_crawl()
            self.results.append(result)
            return result
        except Exception as e:
            error_result = {
                "success": False,
                "source": crawler_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.error(f"Error running crawler {crawler_name}", error=str(e))
            self.results.append(error_result)
            return error_result
    
    def run_all_crawlers(self) -> Dict[str, Any]:
        """Run all crawlers"""
        start_time = datetime.utcnow()
        self.results = []
        
        logger.info(f"Starting crawl of {len(self.crawlers)} sources")
        
        successful_crawls = 0
        failed_crawls = 0
        total_saved = 0
        
        for crawler in self.crawlers:
            try:
                result = crawler.run_crawl()
                self.results.append(result)
                
                if result.get("success"):
                    successful_crawls += 1
                    total_saved += result.get("saved_count", 0)
                else:
                    failed_crawls += 1
                    
            except Exception as e:
                error_result = {
                    "success": False,
                    "source": crawler.name,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.results.append(error_result)
                failed_crawls += 1
                logger.error(f"Error running crawler {crawler.name}", error=str(e))
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "success": True,
            "total_crawlers": len(self.crawlers),
            "successful_crawls": successful_crawls,
            "failed_crawls": failed_crawls,
            "total_announcements_saved": total_saved,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "results": self.results
        }
        
        logger.info("Crawl completed", **summary)
        return summary
    
    def get_crawl_stats(self) -> Dict[str, Any]:
        """Get statistics from last crawl"""
        if not self.results:
            return {
                "message": "No crawls have been run yet",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        successful_results = [r for r in self.results if r.get("success")]
        failed_results = [r for r in self.results if not r.get("success")]
        
        total_saved = sum(r.get("saved_count", 0) for r in successful_results)
        total_duration = sum(r.get("duration_seconds", 0) for r in successful_results)
        
        return {
            "last_crawl_time": max(r.get("timestamp", "") for r in self.results),
            "total_crawlers": len(self.results),
            "successful_crawls": len(successful_results),
            "failed_crawls": len(failed_results),
            "total_announcements_saved": total_saved,
            "average_duration": total_duration / len(successful_results) if successful_results else 0,
            "success_rate": len(successful_results) / len(self.results) * 100,
            "results": self.results
        }
    
    def run_crawler_by_category(self, category: str) -> Dict[str, Any]:
        """Run crawlers that match a specific category"""
        matching_crawlers = [
            crawler for crawler in self.crawlers 
            if category.lower() in [cat.lower() for cat in crawler.categories]
        ]
        
        if not matching_crawlers:
            return {
                "success": False,
                "error": f"No crawlers found for category '{category}'",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        start_time = datetime.utcnow()
        results = []
        
        for crawler in matching_crawlers:
            result = self.run_single_crawler(crawler.name)
            results.append(result)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        successful_crawls = sum(1 for r in results if r.get("success"))
        total_saved = sum(r.get("saved_count", 0) for r in results if r.get("success"))
        
        return {
            "success": True,
            "category": category,
            "crawlers_run": len(matching_crawlers),
            "successful_crawls": successful_crawls,
            "total_announcements_saved": total_saved,
            "duration_seconds": duration,
            "results": results,
            "timestamp": end_time.isoformat()
        }


# Global crawler manager instance
crawler_manager = CrawlerManager()
