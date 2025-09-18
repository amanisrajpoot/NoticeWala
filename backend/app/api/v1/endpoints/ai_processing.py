"""
AI Processing API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.ai_service import ai_service
from app.crawlers.ai_enhanced_crawler import AIEnhancedCrawler
from app.models.announcement import Announcement

logger = structlog.get_logger()
router = APIRouter()


@router.post("/process-content")
async def process_content_with_ai(
    content: str,
    title: str = "",
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Process content using AI for structured data extraction"""
    
    try:
        # Process content with AI
        result = await ai_service.extract_structured_data(content, title)
        
        return {
            "success": True,
            "data": result,
            "processing_method": "openai" if ai_service.openai_client else "fallback"
        }
        
    except Exception as e:
        logger.error(f"AI content processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process content: {str(e)}"
        )


@router.post("/enhance-announcements")
async def enhance_announcements_with_ai(
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Enhance existing announcements with AI processing"""
    
    try:
        # Create AI enhanced crawler
        ai_crawler = AIEnhancedCrawler("ai_enhanced", "https://ai-enhanced.local")
        
        # Run AI processing in background
        background_tasks.add_task(ai_crawler.run_crawl)
        
        return {
            "success": True,
            "message": "AI enhancement process started in background",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"AI enhancement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start AI enhancement: {str(e)}"
        )


@router.post("/detect-duplicates")
async def detect_duplicates_with_ai(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Detect duplicate announcements using AI"""
    
    try:
        # Create AI enhanced crawler
        ai_crawler = AIEnhancedCrawler("ai_enhanced", "https://ai-enhanced.local")
        
        # Detect duplicates
        result = ai_crawler.detect_duplicates()
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect duplicates: {str(e)}"
        )


@router.post("/generate-summary")
async def generate_summary(
    content: str,
    max_length: int = 150,
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Generate AI-powered summary of content"""
    
    try:
        summary = ai_service.generate_summary(content, max_length)
        
        return {
            "success": True,
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary)
        }
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.post("/calculate-similarity")
async def calculate_similarity(
    text1: str,
    text2: str,
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Calculate semantic similarity between two texts"""
    
    try:
        similarity = ai_service.calculate_semantic_similarity(text1, text2)
        
        return {
            "success": True,
            "similarity": similarity,
            "similarity_percentage": round(similarity * 100, 2),
            "text1_length": len(text1),
            "text2_length": len(text2)
        }
        
    except Exception as e:
        logger.error(f"Similarity calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate similarity: {str(e)}"
        )


@router.get("/insights")
async def get_ai_insights(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get AI-generated insights from announcement data"""
    
    try:
        # Create AI enhanced crawler
        ai_crawler = AIEnhancedCrawler("ai_enhanced", "https://ai-enhanced.local")
        
        # Generate insights
        insights = ai_crawler.generate_insights()
        
        return {
            "success": True,
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/status")
async def get_ai_status(
    current_user_id: str = Depends(get_current_user_id_dependency)
):
    """Get AI service status and configuration"""
    
    try:
        status_info = {
            "openai_available": ai_service.openai_client is not None,
            "sentence_transformer_available": ai_service.sentence_transformer is not None,
            "ai_processing_enabled": ai_service.ai_processing_enabled if hasattr(ai_service, 'ai_processing_enabled') else True,
            "model": ai_service.openai_model if hasattr(ai_service, 'openai_model') else "unknown",
            "confidence_threshold": ai_service.confidence_threshold if hasattr(ai_service, 'confidence_threshold') else 0.8
        }
        
        return {
            "success": True,
            "status": status_info
        }
        
    except Exception as e:
        logger.error(f"AI status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI status: {str(e)}"
        )


@router.get("/announcements/{announcement_id}/ai-data")
async def get_announcement_ai_data(
    announcement_id: str,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get AI-processed data for a specific announcement"""
    
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Announcement not found"
            )
        
        # Check if announcement has AI data
        ai_data = {
            "has_ai_data": announcement.confidence and announcement.confidence.get("ai_processed", False),
            "ai_processing_date": announcement.confidence.get("ai_processing_date") if announcement.confidence else None,
            "confidence_scores": announcement.confidence or {},
            "priority_score": announcement.priority_score,
            "categories": announcement.categories,
            "tags": announcement.tags,
            "exam_dates": announcement.exam_dates,
            "eligibility": announcement.eligibility,
            "location": announcement.location
        }
        
        return {
            "success": True,
            "announcement_id": announcement_id,
            "ai_data": ai_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI data for announcement {announcement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI data: {str(e)}"
        )
