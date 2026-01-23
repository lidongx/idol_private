"""
IdolMoment models for idol social moments system
Story 5.2: 偶像朋友圈系统
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class IdolMoment(Base):
    """
    IdolMoment model for idol social moments (like WeChat Moments)

    Represents a single post/moment shared by an idol with users.
    """
    __tablename__ = "idol_moments"

    id = Column(Integer, primary_key=True, index=True)
    idol_id = Column(Integer, ForeignKey("idols.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    likes_count = Column(Integer, default=0, nullable=False)
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    idol = relationship("Idol", back_populates="moments")
    likes = relationship("IdolMomentLike", back_populates="moment", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint('char_length(content) <= 300', name='check_content_length'),
        CheckConstraint('likes_count >= 0', name='check_likes_count_non_negative'),
    )

    @property
    def relative_time(self) -> str:
        """Get relative time string (e.g., '2小时前', '昨天')"""
        if not self.posted_at:
            return ""

        now = datetime.utcnow()
        delta = now - self.posted_at

        if delta.days == 0:
            # Today
            hours = delta.seconds // 3600
            if hours == 0:
                minutes = delta.seconds // 60
                if minutes == 0:
                    return "刚刚"
                return f"{minutes}分钟前"
            return f"{hours}小时前"
        elif delta.days == 1:
            return "昨天"
        elif delta.days < 7:
            return f"{delta.days}天前"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks}周前"
        else:
            # Format as MM-DD
            return self.posted_at.strftime("%m月%d日")

    def increment_likes(self):
        """Increment like count"""
        self.likes_count += 1

    def decrement_likes(self):
        """Decrement like count (for unlike)"""
        if self.likes_count > 0:
            self.likes_count -= 1

    def __repr__(self):
        return f"<IdolMoment(id={self.id}, idol_id={self.idol_id}, posted_at={self.posted_at})>"


class IdolMomentLike(Base):
    """
    IdolMomentLike model for tracking user likes on idol moments
    """
    __tablename__ = "idol_moment_likes"

    id = Column(Integer, primary_key=True, index=True)
    moment_id = Column(Integer, ForeignKey("idol_moments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    liked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    moment = relationship("IdolMoment", back_populates="likes")
    user = relationship("User", back_populates="moment_likes")

    # Constraints - each user can only like a moment once
    __table_args__ = (
        UniqueConstraint('moment_id', 'user_id', name='uq_moment_user_like'),
    )

    def __repr__(self):
        return f"<IdolMomentLike(moment_id={self.moment_id}, user_id={self.user_id})>"
