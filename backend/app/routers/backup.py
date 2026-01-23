"""
Data Backup and Export API router
Story 8.3: 云端备份与数据导出
"""
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.backup_service import BackupService


router = APIRouter(prefix="/backup", tags=["backup"])


# Response models
class BackupStatsResponse(BaseModel):
    """Response model for backup statistics"""
    user_id: int
    conversation_count: int
    message_count: int
    memory_count: int
    achievement_count: int
    milestone_count: int
    subscription_tier: str
    created_at: str


class ExportDataResponse(BaseModel):
    """Response model for data export"""
    success: bool
    message: str
    filename: str
    file_size_bytes: int
    expires_at: str
    download_url: str


@router.get(
    "/stats",
    response_model=BackupStatsResponse,
    summary="获取数据统计",
    description="获取用户数据统计信息（对话、消息、记忆等数量）"
)
def get_backup_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user data statistics

    Returns:
    - conversation_count: Number of conversations
    - message_count: Total number of messages
    - memory_count: Number of memories
    - achievement_count: Number of unlocked achievements
    - milestone_count: Number of milestones
    """
    backup_service = BackupService(db)

    try:
        stats = backup_service.get_backup_stats(current_user.id)
        return BackupStatsResponse(**stats)

    except Exception as e:
        print(f"Error getting backup stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据统计失败"
        )


@router.post(
    "/export",
    response_model=ExportDataResponse,
    summary="导出用户数据",
    description="导出完整用户数据为JSON文件（对话、记忆、成就等）"
)
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export complete user data to JSON file

    Export includes:
    - User profile
    - All conversations and messages
    - All memories
    - Intimacy progress
    - Unlocked achievements
    - Milestones

    Returns:
    - filename: Name of the exported file
    - file_size_bytes: File size in bytes
    - expires_at: Expiration time (24 hours from now)
    - download_url: URL to download the file
    """
    backup_service = BackupService(db)

    try:
        # Generate export file
        filepath = backup_service.save_backup_to_file(
            user_id=current_user.id,
            backup_dir="backups/exports"
        )

        # Get file info
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        # Calculate expiration (24 hours from now)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        return ExportDataResponse(
            success=True,
            message="数据导出成功",
            filename=filename,
            file_size_bytes=file_size,
            expires_at=expires_at.isoformat(),
            download_url=f"/api/v1/backup/download/{filename}"
        )

    except Exception as e:
        print(f"Error exporting user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据导出失败"
        )


@router.get(
    "/download/{filename}",
    summary="下载导出文件",
    description="下载已导出的数据文件（24小时内有效）"
)
def download_export_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download exported data file

    Path params:
    - filename: Name of the file to download

    Returns:
    - File download response (JSON file)

    Note:
    - Files are valid for 24 hours after export
    - Only the owner can download their own export
    """
    # Security: Verify filename belongs to current user
    if not filename.startswith(f"user_{current_user.id}_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该文件"
        )

    # Check if file exists
    filepath = os.path.join("backups/exports", filename)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或已过期"
        )

    # Check file age (24 hours)
    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    if datetime.now() - file_mtime > timedelta(hours=24):
        # File expired, delete it
        os.remove(filepath)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="文件已过期"
        )

    # Return file for download
    return FileResponse(
        path=filepath,
        media_type="application/json",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.delete(
    "/download/{filename}",
    summary="删除导出文件",
    description="删除已导出的数据文件"
)
def delete_export_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete exported data file

    Path params:
    - filename: Name of the file to delete

    Returns:
    - Success message
    """
    # Security: Verify filename belongs to current user
    if not filename.startswith(f"user_{current_user.id}_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该文件"
        )

    # Check if file exists
    filepath = os.path.join("backups/exports", filename)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # Delete file
    try:
        os.remove(filepath)
        return {
            "success": True,
            "message": "文件已删除"
        }
    except Exception as e:
        print(f"Error deleting export file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除文件失败"
        )
