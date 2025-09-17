"""
Users API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog
import uuid

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user_id_dependency
from app.models.user import User, PushToken
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdate, PushTokenCreate

logger = structlog.get_logger()
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    
    try:
        # Convert string user_id back to UUID for database query
        user_uuid = uuid.UUID(current_user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user profile", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    try:
        user_uuid = uuid.UUID(current_user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if user_update.first_name is not None:
            user.first_name = user_update.first_name
        if user_update.last_name is not None:
            user.last_name = user_update.last_name
        if user_update.username is not None:
            # Check if username is already taken
            existing_user = db.query(User).filter(
                User.username == user_update.username,
                User.id != current_user_id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_update.username
        
        db.commit()
        db.refresh(user)
        
        logger.info("User profile updated", user_id=str(user.id))
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user profile", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.post("/push-token")
async def register_push_token(
    token_data: PushTokenCreate,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Register push notification token for user"""
    
    try:
        # Check if token already exists
        existing_token = db.query(PushToken).filter(
            PushToken.token == token_data.token
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.user_id = current_user_id
            existing_token.platform = token_data.platform
            existing_token.device_id = token_data.device_id
            existing_token.app_version = token_data.app_version
            existing_token.os_version = token_data.os_version
            existing_token.is_active = True
        else:
            # Create new token
            push_token = PushToken(
                user_id=current_user_id,
                token=token_data.token,
                platform=token_data.platform,
                device_id=token_data.device_id,
                app_version=token_data.app_version,
                os_version=token_data.os_version
            )
            db.add(push_token)
        
        db.commit()
        
        logger.info("Push token registered", user_id=current_user_id, platform=token_data.platform)
        
        return {"message": "Push token registered successfully"}
        
    except Exception as e:
        logger.error("Failed to register push token", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register push token"
        )


@router.delete("/push-token/{token}")
async def unregister_push_token(
    token: str,
    current_user_id: str = Depends(get_current_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Unregister push notification token"""
    
    try:
        push_token = db.query(PushToken).filter(
            PushToken.token == token,
            PushToken.user_id == current_user_id
        ).first()
        
        if not push_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Push token not found"
            )
        
        db.delete(push_token)
        db.commit()
        
        logger.info("Push token unregistered", user_id=current_user_id, token=token)
        
        return {"message": "Push token unregistered successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to unregister push token", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unregister push token"
        )
