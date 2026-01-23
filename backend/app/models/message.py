"""
Message SQLAlchemy Model
Stores individual messages within conversations
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    """Message model for individual chat messages"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联对话ID")
    sender_type = Column(String(20), nullable=False, comment="发送者类型: user/idol")
    message_type = Column(String(20), default="text", nullable=False, comment="消息类型: text/voice/image/emoji")
    content = Column(Text, nullable=False, comment="消息内容")
    voice_url = Column(String(500), nullable=True, comment="语音消息URL")
    voice_duration = Column(Integer, nullable=True, comment="语音时长(秒)")
    emotion = Column(String(50), nullable=True, comment="情绪标签")
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True, comment="发送时间")
    status = Column(String(20), default="sent", nullable=False, comment="消息状态: sent/delivered/read")

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender={self.sender_type})>"
