"""
Offline Synchronization API Endpoints

Handles offline-first mobile app synchronization, conflict resolution,
and data consistency across online/offline states.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.services.offline_sync_service import offline_sync_service
from app.schemas.offline_sync import (
    SyncRequest,
    SyncResponse,
    OfflineChangesRequest,
    OfflineChangesResponse,
    SyncStatusResponse
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/sync", response_model=SyncResponse)
async def sync_offline_data(
    request: SyncRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Synchronize offline data with server.
    
    This endpoint handles both pulling data for offline use and
    pushing changes made while offline.
    """
    try:
        logger.info("Starting offline sync", 
                   user_id=current_user_id, 
                   sync_type=request.sync_type)
        
        # Get sync data from server
        sync_data = await offline_sync_service.get_sync_data(
            db=db,
            user_id=current_user_id,
            last_sync_timestamp=request.last_sync_timestamp,
            sync_type=request.sync_type
        )
        
        # Process offline changes if provided
        sync_results = None
        if request.offline_changes:
            sync_results = await offline_sync_service.process_offline_changes(
                db=db,
                user_id=current_user_id,
                offline_changes=request.offline_changes
            )
        
        response = SyncResponse(
            success=True,
            sync_id=sync_data["sync_id"],
            timestamp=sync_data["timestamp"],
            sync_type=sync_data["sync_type"],
            data=sync_data["data"],
            metadata=sync_data["metadata"],
            sync_results=sync_results
        )
        
        logger.info("Offline sync completed", 
                   user_id=current_user_id, 
                   sync_id=sync_data["sync_id"])
        
        return response
        
    except Exception as e:
        logger.error("Offline sync failed", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/changes", response_model=OfflineChangesResponse)
async def submit_offline_changes(
    request: OfflineChangesRequest,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Submit changes made while offline for processing and conflict resolution.
    """
    try:
        logger.info("Processing offline changes", 
                   user_id=current_user_id, 
                   change_count=len(request.changes))
        
        sync_results = await offline_sync_service.process_offline_changes(
            db=db,
            user_id=current_user_id,
            offline_changes=request.changes
        )
        
        response = OfflineChangesResponse(
            success=True,
            processed=sync_results["processed"],
            successful=sync_results["successful"],
            conflicts=sync_results["conflicts"],
            errors=sync_results["errors"]
        )
        
        logger.info("Offline changes processed", 
                   user_id=current_user_id, 
                   results=sync_results)
        
        return response
        
    except Exception as e:
        logger.error("Failed to process offline changes", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process changes: {str(e)}"
        )


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Get current synchronization status for the user.
    """
    try:
        status_data = await offline_sync_service.get_sync_status(
            db=db,
            user_id=current_user_id
        )
        
        if "error" in status_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=status_data["error"]
            )
        
        return SyncStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get sync status", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}"
        )


@router.get("/conflicts")
async def get_sync_conflicts(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Get pending synchronization conflicts that need user resolution.
    """
    try:
        # This would typically query a conflicts table
        # For now, return empty list as conflicts are resolved automatically
        conflicts = []
        
        return {
            "conflicts": conflicts,
            "total_count": len(conflicts)
        }
        
    except Exception as e:
        logger.error("Failed to get sync conflicts", 
                    user_id=current_user_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conflicts: {str(e)}"
        )


@router.post("/resolve-conflict")
async def resolve_sync_conflict(
    conflict_id: str,
    resolution: str = Query(..., description="Resolution strategy: server_wins, client_wins, merge"),
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """
    Resolve a specific synchronization conflict.
    """
    try:
        # This would implement conflict resolution logic
        # For now, return success
        return {
            "success": True,
            "conflict_id": conflict_id,
            "resolution": resolution,
            "message": "Conflict resolved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to resolve conflict", 
                    user_id=current_user_id, 
                    conflict_id=conflict_id, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflict: {str(e)}"
        )


@router.get("/health")
async def sync_health_check():
    """
    Health check for offline sync service.
    """
    return {
        "status": "healthy",
        "service": "offline_sync",
        "timestamp": datetime.utcnow().isoformat()
    }
