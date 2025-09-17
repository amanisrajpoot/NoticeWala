"""
Crawlers API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.crawlers.crawler_manager import crawler_manager

logger = structlog.get_logger()
router = APIRouter()


@router.get("/list")
async def list_crawlers():
    """List all available crawlers"""
    try:
        crawlers = crawler_manager.list_crawlers()
        return {
            "success": True,
            "crawlers": crawlers,
            "count": len(crawlers)
        }
    except Exception as e:
        logger.error("Error listing crawlers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list crawlers"
        )


@router.post("/run/{crawler_name}")
async def run_crawler(
    crawler_name: str,
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Run a specific crawler"""
    try:
        logger.info(f"Running crawler: {crawler_name} by user: {current_user_id}")
        result = crawler_manager.run_single_crawler(crawler_name)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Crawler '{crawler_name}' completed successfully",
                "result": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Crawler '{crawler_name}' failed: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running crawler {crawler_name}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run crawler"
        )


@router.post("/run-all")
async def run_all_crawlers(
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Run all available crawlers"""
    try:
        logger.info(f"Running all crawlers by user: {current_user_id}")
        result = crawler_manager.run_all_crawlers()
        
        return {
            "success": True,
            "message": "All crawlers completed",
            "summary": {
                "total_crawlers": result.get("total_crawlers", 0),
                "successful_crawls": result.get("successful_crawls", 0),
                "failed_crawls": result.get("failed_crawls", 0),
                "total_announcements_saved": result.get("total_announcements_saved", 0),
                "duration_seconds": result.get("duration_seconds", 0)
            },
            "results": result.get("results", [])
        }
            
    except Exception as e:
        logger.error("Error running all crawlers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run crawlers"
        )


@router.post("/run-by-category")
async def run_crawlers_by_category(
    category: str = Query(..., description="Category to run crawlers for"),
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Run crawlers that match a specific category"""
    try:
        logger.info(f"Running crawlers for category: {category} by user: {current_user_id}")
        result = crawler_manager.run_crawler_by_category(category)
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Crawlers for category '{category}' completed",
                "result": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No crawlers found for category '{category}'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running crawlers for category {category}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run crawlers"
        )


@router.get("/stats")
async def get_crawl_stats(
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Get crawling statistics"""
    try:
        stats = crawler_manager.get_crawl_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error("Error getting crawl stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get crawl statistics"
        )
