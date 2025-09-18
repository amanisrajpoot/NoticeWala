"""
Pydantic schemas for offline synchronization functionality.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SyncRequest(BaseModel):
    """Request schema for offline data synchronization."""
    sync_type: str = Field("incremental", description="Type of sync: full, incremental, delta")
    last_sync_timestamp: Optional[datetime] = Field(None, description="Last successful sync timestamp")
    offline_changes: Optional[List[Dict[str, Any]]] = Field(None, description="Changes made while offline")
    device_id: Optional[str] = Field(None, description="Device identifier for conflict resolution")
    app_version: Optional[str] = Field(None, description="App version for compatibility checks")


class OfflineChange(BaseModel):
    """Schema for a single offline change."""
    id: str = Field(..., description="Unique identifier for the change")
    type: str = Field(..., description="Type of change: user_interaction, preference_update, subscription_update")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the change was made")
    data: Dict[str, Any] = Field(..., description="Change data")
    device_id: Optional[str] = Field(None, description="Device that made the change")
    version: Optional[str] = Field("1.0", description="Change version for conflict resolution")


class OfflineChangesRequest(BaseModel):
    """Request schema for submitting offline changes."""
    changes: List[OfflineChange] = Field(..., description="List of changes made while offline")
    device_id: Optional[str] = Field(None, description="Device identifier")
    sync_id: Optional[str] = Field(None, description="Sync session identifier")


class SyncData(BaseModel):
    """Schema for synchronized data."""
    announcements: List[Dict[str, Any]] = Field(..., description="Announcement data")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    subscriptions: List[Dict[str, Any]] = Field(default_factory=list, description="User subscriptions")


class SyncMetadata(BaseModel):
    """Schema for sync metadata."""
    total_announcements: int = Field(..., description="Total number of announcements in sync")
    has_more: bool = Field(False, description="Whether there are more items to sync")
    sync_version: str = Field("1.0", description="Sync protocol version")
    server_time: datetime = Field(default_factory=datetime.utcnow, description="Server timestamp")


class SyncResult(BaseModel):
    """Schema for individual sync operation result."""
    change_id: str = Field(..., description="ID of the processed change")
    status: str = Field(..., description="Result status: success, conflict, error")
    message: Optional[str] = Field(None, description="Result message")
    error: Optional[str] = Field(None, description="Error message if failed")


class SyncResults(BaseModel):
    """Schema for sync operation results."""
    processed: int = Field(0, description="Number of changes processed")
    successful: List[SyncResult] = Field(default_factory=list, description="Successfully processed changes")
    conflicts: List[SyncResult] = Field(default_factory=list, description="Changes with conflicts")
    errors: List[SyncResult] = Field(default_factory=list, description="Failed changes")


class SyncResponse(BaseModel):
    """Response schema for sync operations."""
    success: bool = Field(..., description="Whether the sync was successful")
    sync_id: str = Field(..., description="Unique sync session identifier")
    timestamp: str = Field(..., description="Sync timestamp")
    sync_type: str = Field(..., description="Type of sync performed")
    data: SyncData = Field(..., description="Synchronized data")
    metadata: SyncMetadata = Field(..., description="Sync metadata")
    sync_results: Optional[SyncResults] = Field(None, description="Results of processing offline changes")


class OfflineChangesResponse(BaseModel):
    """Response schema for offline changes processing."""
    success: bool = Field(..., description="Whether processing was successful")
    processed: int = Field(0, description="Number of changes processed")
    successful: List[SyncResult] = Field(default_factory=list, description="Successfully processed changes")
    conflicts: List[SyncResult] = Field(default_factory=list, description="Changes with conflicts")
    errors: List[SyncResult] = Field(default_factory=list, description="Failed changes")


class SyncStatusResponse(BaseModel):
    """Response schema for sync status."""
    user_id: str = Field(..., description="User ID")
    last_sync: Optional[str] = Field(None, description="Last sync timestamp")
    pending_changes: int = Field(0, description="Number of pending changes")
    sync_status: str = Field("ready", description="Current sync status")
    server_time: str = Field(..., description="Current server time")


class ConflictResolution(BaseModel):
    """Schema for conflict resolution."""
    conflict_id: str = Field(..., description="ID of the conflict to resolve")
    resolution: str = Field(..., description="Resolution strategy: server_wins, client_wins, merge")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom resolution data")


class SyncHealthCheck(BaseModel):
    """Schema for sync service health check."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Health check timestamp")
    version: Optional[str] = Field(None, description="Service version")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency status")


# Mobile-specific schemas
class MobileSyncConfig(BaseModel):
    """Configuration for mobile app synchronization."""
    sync_interval: int = Field(300, description="Sync interval in seconds")
    max_offline_days: int = Field(7, description="Maximum days to store offline data")
    conflict_resolution: str = Field("server_wins", description="Default conflict resolution strategy")
    auto_sync: bool = Field(True, description="Whether to enable automatic sync")
    wifi_only: bool = Field(False, description="Whether to sync only on WiFi")
    background_sync: bool = Field(True, description="Whether to enable background sync")


class DeviceInfo(BaseModel):
    """Schema for device information."""
    device_id: str = Field(..., description="Unique device identifier")
    platform: str = Field(..., description="Device platform (iOS, Android)")
    app_version: str = Field(..., description="App version")
    os_version: str = Field(..., description="Operating system version")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen timestamp")
    sync_capabilities: List[str] = Field(default_factory=list, description="Supported sync features")


class OfflineStorageInfo(BaseModel):
    """Information about offline storage usage."""
    total_size: int = Field(..., description="Total storage size in bytes")
    used_size: int = Field(..., description="Used storage size in bytes")
    available_size: int = Field(..., description="Available storage size in bytes")
    announcement_count: int = Field(0, description="Number of announcements stored offline")
    last_cleanup: Optional[datetime] = Field(None, description="Last cleanup timestamp")
    cleanup_threshold: int = Field(100 * 1024 * 1024, description="Cleanup threshold in bytes")  # 100MB
