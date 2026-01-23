"""
Conversation SQLAlchemy Model
Stores user-idol conversation sessions
"""
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    """Conversation model for user-idol chat sessions"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联用户ID")
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False, comment="关联偶像ID")
    intimacy_level = Column(Integer, default=1, nullable=False, comment="亲密度等级(1-100)")
    intimacy_exp = Column(Integer, default=0, nullable=False, comment="亲密度经验值")
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, comment="创建时间")
    last_message_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True, comment="最后消息时间")
    last_active_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True, comment="最后活跃时间（心跳更新）")

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'idol_id', name='unique_user_idol'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, idol_id={self.idol_id}, level={self.intimacy_level})>"
