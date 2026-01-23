"""
Data Backup and Export Service
Story 8.3: 云端备份与数据导出
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.memory import Memory
from app.models.intimacy import Intimacy
from app.models.achievement import UserAchievement, Achievement
from app.models.milestone import Milestone


class BackupService:
    """
    Service for backing up and exporting user data
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user_backup(self, user_id: int) -> Dict[str, Any]:
        """
        Create a complete backup of user's data

        Args:
            user_id: User ID

        Returns:
            dict: User data in JSON-serializable format

        Backup includes:
        - User profile
        - Conversations and messages
        - Memories
        - Intimacy progress
        - Achievements
        - Milestones
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        backup_data = {
            "backup_version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "user": self._export_user_profile(user),
            "conversations": self._export_conversations(user_id),
            "memories": self._export_memories(user_id),
            "intimacy": self._export_intimacy(user_id),
            "achievements": self._export_achievements(user_id),
            "milestones": self._export_milestones(user_id),
        }

        return backup_data

    def _export_user_profile(self, user: User) -> Dict[str, Any]:
        """Export user profile data"""
        return {
            "id": user.id,
            "phone": user.phone,
            "username": user.username,
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "subscription_expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            "created_at": user.created_at.isoformat(),
            "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
        }

    def _export_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """Export all conversations with messages"""
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        result = []
        for conv in conversations:
            # Get all messages for this conversation
            messages = self.db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.timestamp.asc()).all()

            conv_data = {
                "id": conv.id,
                "idol_id": conv.idol_id,
                "created_at": conv.created_at.isoformat(),
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "messages": [
                    {
                        "id": msg.id,
                        "sender_type": msg.sender_type,
                        "content": msg.content,
                        "emotion": msg.emotion,
                        "timestamp": msg.timestamp.isoformat(),
                        "status": msg.status,
                    }
                    for msg in messages
                ]
            }
            result.append(conv_data)

        return result

    def _export_memories(self, user_id: int) -> List[Dict[str, Any]]:
        """Export all memories"""
        memories = self.db.query(Memory).filter(
            Memory.user_id == user_id
        ).all()

        return [
            {
                "id": mem.id,
                "content": mem.content,
                "memory_type": mem.memory_type,
                "importance": mem.importance,
                "mentioned_count": mem.mentioned_count,
                "last_mentioned_at": mem.last_mentioned_at.isoformat() if mem.last_mentioned_at else None,
                "created_at": mem.created_at.isoformat(),
            }
            for mem in memories
        ]

    def _export_intimacy(self, user_id: int) -> List[Dict[str, Any]]:
        """Export intimacy progress for all conversations"""
        intimacy_records = self.db.query(Intimacy).join(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        return [
            {
                "conversation_id": inti.conversation_id,
                "current_level": inti.current_level,
                "current_exp": inti.current_exp,
                "total_exp": inti.total_exp,
                "last_interaction_at": inti.last_interaction_at.isoformat() if inti.last_interaction_at else None,
                "created_at": inti.created_at.isoformat(),
            }
            for inti in intimacy_records
        ]

    def _export_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Export unlocked achievements"""
        user_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()

        result = []
        for ua in user_achievements:
            achievement = self.db.query(Achievement).filter(
                Achievement.id == ua.achievement_id
            ).first()

            if achievement:
                result.append({
                    "achievement_id": ua.achievement_id,
                    "achievement_name": achievement.achievement_name,
                    "achievement_description": achievement.achievement_description,
                    "achievement_icon": achievement.achievement_icon,
                    "reward_exp": achievement.reward_exp,
                    "unlocked_at": ua.unlocked_at.isoformat(),
                })

        return result

    def _export_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """Export milestones"""
        milestones = self.db.query(Milestone).filter(
            Milestone.user_id == user_id
        ).all()

        return [
            {
                "id": ms.id,
                "title": ms.title,
                "description": ms.description,
                "milestone_date": ms.milestone_date.isoformat(),
                "milestone_type": ms.milestone_type,
                "anniversary_count": ms.anniversary_count,
                "last_celebrated_at": ms.last_celebrated_at.isoformat() if ms.last_celebrated_at else None,
                "created_at": ms.created_at.isoformat(),
            }
            for ms in milestones
        ]

    def save_backup_to_file(self, user_id: int, backup_dir: str = "backups") -> str:
        """
        Save user backup to JSON file

        Args:
            user_id: User ID
            backup_dir: Directory to save backup files (default: "backups")

        Returns:
            str: Backup file path

        File naming: backups/user_{user_id}_{timestamp}.json
        """
        # Create backup directory if not exists
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup data
        backup_data = self.create_user_backup(user_id)

        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"user_{user_id}_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        print(f"[Backup] Saved backup for user {user_id} to {filepath}")
        return filepath

    def get_backup_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about user's data for backup info

        Args:
            user_id: User ID

        Returns:
            dict: Statistics about user's data
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Count conversations and messages
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        total_messages = 0
        for conv in conversations:
            message_count = self.db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            total_messages += message_count

        # Count memories
        memory_count = self.db.query(Memory).filter(
            Memory.user_id == user_id
        ).count()

        # Count achievements
        achievement_count = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).count()

        # Count milestones
        milestone_count = self.db.query(Milestone).filter(
            Milestone.user_id == user_id
        ).count()

        return {
            "user_id": user_id,
            "conversation_count": len(conversations),
            "message_count": total_messages,
            "memory_count": memory_count,
            "achievement_count": achievement_count,
            "milestone_count": milestone_count,
            "subscription_tier": user.subscription_tier,
            "created_at": user.created_at.isoformat(),
        }
