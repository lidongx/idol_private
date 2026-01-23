"""
Memory model for long-term user memory storage
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Memory(Base):
    """User memory model"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(String(50))  # hobby, work, family, feeling, goal, preference, event
    importance = Column(String(20), default="medium")  # low, medium, high
    source_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    embedding_id = Column(String(100))  # ChromaDB document ID
    created_at = Column(DateTime, default=datetime.utcnow)
    last_mentioned_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")
    source_message = relationship("Message", foreign_keys=[source_message_id])
    proactive_mentions = relationship("ProactiveMention", back_populates="memory", cascade="all, delete-orphan")

    @property
    def is_recent(self) -> bool:
        """Check if memory was created in last 7 days"""
        if not self.created_at:
            return False
        delta = datetime.utcnow() - self.created_at
        return delta.days <= 7

    @property
    def is_frequently_mentioned(self) -> bool:
        """Check if memory was mentioned in last 7 days"""
        if not self.last_mentioned_at:
            return False
        delta = datetime.utcnow() - self.last_mentioned_at
        return delta.days <= 7

    def mark_mentioned(self):
        """Update last_mentioned_at timestamp"""
        self.last_mentioned_at = datetime.utcnow()

    def __repr__(self):
        return f"<Memory(id={self.id}, user_id={self.user_id}, type={self.memory_type}, importance={self.importance})>"


class MemoryTag(Base):
    """User profile tags and attributes"""
    __tablename__ = "memory_tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(50), nullable=False)  # name, job, city, birthday, hobby, etc.
    tag_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memory_tags")

    def __repr__(self):
        return f"<MemoryTag(user_id={self.user_id}, tag={self.tag_name}, value={self.tag_value})>"
