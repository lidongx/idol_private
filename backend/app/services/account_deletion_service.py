"""
Account Deletion Service
Story 8.4: 账号删除与数据清除
"""
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.account_deletion import AccountDeletionRequest
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.memory import Memory
from app.models.intimacy import Intimacy
from app.models.achievement import UserAchievement
from app.models.milestone import Milestone
from app.models.user_device import UserDevice
from app.services.backup_service import BackupService


class AccountDeletionService:
    """
    Service for handling account deletion with 7-day cooling-off period
    """

    COOLING_OFF_DAYS = 7  # 7-day cooling-off period

    def __init__(self, db: Session):
        self.db = db

    def create_deletion_request(
        self,
        user_id: int,
        reason: Optional[str] = None,
        detailed_reason: Optional[str] = None
    ) -> AccountDeletionRequest:
        """
        Create account deletion request with 7-day cooling-off period

        Args:
            user_id: User ID
            reason: Deletion reason (optional)
            detailed_reason: Detailed explanation (optional)

        Returns:
            AccountDeletionRequest: Created deletion request

        Raises:
            ValueError: If user not found or already has pending request
        """
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check if there's already a pending request
        existing_request = self.db.query(AccountDeletionRequest).filter(
            AccountDeletionRequest.user_id == user_id,
            AccountDeletionRequest.status == 'pending'
        ).first()

        if existing_request:
            raise ValueError("已存在待处理的删除请求，请先取消之前的请求")

        # Calculate scheduled deletion date (7 days from now)
        scheduled_deletion_at = datetime.utcnow() + timedelta(days=self.COOLING_OFF_DAYS)

        # Create deletion request
        deletion_request = AccountDeletionRequest(
            user_id=user_id,
            status='pending',
            reason=reason,
            detailed_reason=detailed_reason,
            scheduled_deletion_at=scheduled_deletion_at
        )

        self.db.add(deletion_request)
        self.db.commit()
        self.db.refresh(deletion_request)

        print(f"[Account Deletion] Created deletion request for user {user_id}, scheduled for {scheduled_deletion_at.isoformat()}")

        return deletion_request

    def cancel_deletion_request(self, user_id: int) -> Dict[str, Any]:
        """
        Cancel pending deletion request (only during cooling-off period)

        Args:
            user_id: User ID

        Returns:
            dict: Result message

        Raises:
            ValueError: If no pending request or cooling-off period expired
        """
        # Find pending request
        deletion_request = self.db.query(AccountDeletionRequest).filter(
            AccountDeletionRequest.user_id == user_id,
            AccountDeletionRequest.status == 'pending'
        ).first()

        if not deletion_request:
            raise ValueError("没有待处理的删除请求")

        if not deletion_request.can_cancel:
            raise ValueError("冷静期已过，无法取消删除请求")

        # Cancel request
        deletion_request.status = 'cancelled'
        deletion_request.updated_at = datetime.utcnow()

        self.db.commit()

        print(f"[Account Deletion] User {user_id} cancelled deletion request")

        return {
            "success": True,
            "message": "删除请求已取消"
        }

    def get_deletion_request(self, user_id: int) -> Optional[AccountDeletionRequest]:
        """
        Get pending deletion request for user

        Args:
            user_id: User ID

        Returns:
            AccountDeletionRequest or None
        """
        return self.db.query(AccountDeletionRequest).filter(
            AccountDeletionRequest.user_id == user_id,
            AccountDeletionRequest.status == 'pending'
        ).first()

    def permanently_delete_account(self, user_id: int, deletion_request_id: int) -> Dict[str, Any]:
        """
        Permanently delete user account and all associated data

        This method:
        1. Creates final backup
        2. Deletes all user data from database
        3. Deletes backup files
        4. Marks deletion request as completed

        Args:
            user_id: User ID
            deletion_request_id: Deletion request ID

        Returns:
            dict: Deletion summary

        Raises:
            ValueError: If user not found or deletion not authorized
        """
        # Get deletion request
        deletion_request = self.db.query(AccountDeletionRequest).filter(
            AccountDeletionRequest.id == deletion_request_id,
            AccountDeletionRequest.user_id == user_id
        ).first()

        if not deletion_request:
            raise ValueError("删除请求不存在")

        if not deletion_request.is_ready_for_deletion:
            raise ValueError("删除请求尚未到期，请等待冷静期结束")

        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        print(f"[Account Deletion] Starting permanent deletion for user {user_id}")

        # Step 1: Create final backup
        if not deletion_request.backup_created:
            try:
                backup_service = BackupService(self.db)
                backup_filepath = backup_service.save_backup_to_file(
                    user_id=user_id,
                    backup_dir="backups/deletions"
                )
                deletion_request.backup_created = True
                deletion_request.backup_filepath = backup_filepath
                self.db.commit()
                print(f"[Account Deletion] Created final backup: {backup_filepath}")
            except Exception as e:
                print(f"[Account Deletion] Error creating backup: {e}")
                # Continue with deletion even if backup fails

        # Step 2: Delete all user data from database
        deletion_summary = self._delete_all_user_data(user_id)

        # Step 3: Delete backup files
        self._delete_backup_files(user_id)

        # Step 4: Mark deletion request as completed
        deletion_request.status = 'completed'
        deletion_request.completed_at = datetime.utcnow()
        self.db.commit()

        print(f"[Account Deletion] Completed permanent deletion for user {user_id}")

        return {
            "success": True,
            "message": "账号已永久删除",
            "user_id": user_id,
            "summary": deletion_summary,
            "completed_at": deletion_request.completed_at.isoformat()
        }

    def _delete_all_user_data(self, user_id: int) -> Dict[str, int]:
        """
        Delete all data associated with user

        Args:
            user_id: User ID

        Returns:
            dict: Deletion counts for each data type
        """
        summary = {}

        # Delete conversations and messages
        conversations = self.db.query(Conversation).filter(Conversation.user_id == user_id).all()
        message_count = 0
        for conv in conversations:
            message_count += self.db.query(Message).filter(Message.conversation_id == conv.id).delete()
        conversation_count = self.db.query(Conversation).filter(Conversation.user_id == user_id).delete()
        summary['conversations'] = conversation_count
        summary['messages'] = message_count

        # Delete memories
        memory_count = self.db.query(Memory).filter(Memory.user_id == user_id).delete()
        summary['memories'] = memory_count

        # Delete intimacy records
        intimacy_count = self.db.query(Intimacy).join(Conversation).filter(
            Conversation.user_id == user_id
        ).delete(synchronize_session=False)
        summary['intimacy_records'] = intimacy_count

        # Delete achievements
        achievement_count = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).delete()
        summary['achievements'] = achievement_count

        # Delete milestones
        milestone_count = self.db.query(Milestone).filter(Milestone.user_id == user_id).delete()
        summary['milestones'] = milestone_count

        # Delete devices
        device_count = self.db.query(UserDevice).filter(UserDevice.user_id == user_id).delete()
        summary['devices'] = device_count

        # Delete user account
        user_deleted = self.db.query(User).filter(User.id == user_id).delete()
        summary['user'] = user_deleted

        self.db.commit()

        return summary

    def _delete_backup_files(self, user_id: int):
        """
        Delete all backup files for user

        Args:
            user_id: User ID
        """
        # Delete daily backups
        daily_pattern = f"backups/daily/user_{user_id}_*.json"
        for filepath in glob.glob(daily_pattern):
            try:
                os.remove(filepath)
                print(f"[Account Deletion] Deleted backup: {filepath}")
            except Exception as e:
                print(f"[Account Deletion] Error deleting {filepath}: {e}")

        # Delete export files
        export_pattern = f"backups/exports/user_{user_id}_*.json"
        for filepath in glob.glob(export_pattern):
            try:
                os.remove(filepath)
                print(f"[Account Deletion] Deleted export: {filepath}")
            except Exception as e:
                print(f"[Account Deletion] Error deleting {filepath}: {e}")

        # Delete deletion backups
        deletion_pattern = f"backups/deletions/user_{user_id}_*.json"
        for filepath in glob.glob(deletion_pattern):
            try:
                os.remove(filepath)
                print(f"[Account Deletion] Deleted deletion backup: {filepath}")
            except Exception as e:
                print(f"[Account Deletion] Error deleting {filepath}: {e}")

    def get_pending_deletions(self) -> list[AccountDeletionRequest]:
        """
        Get all pending deletion requests that are ready for execution

        Returns:
            list: List of deletion requests ready for deletion
        """
        now = datetime.utcnow()
        return self.db.query(AccountDeletionRequest).filter(
            AccountDeletionRequest.status == 'pending',
            AccountDeletionRequest.scheduled_deletion_at <= now
        ).all()
