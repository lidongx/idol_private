"""
Idol Model
Represents AI idol characters with personality and profile data
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Idol(Base):
    """
    Idol character model

    Represents an AI idol with personality, appearance, and background information.
    Used for conversation context and user interaction.
    """
    __tablename__ = "idols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    personality_prompt = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    hobbies = Column(Text, nullable=True)
    background_story = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    state = relationship("IdolState", back_populates="idol", uselist=False, cascade="all, delete-orphan")
    moments = relationship("IdolMoment", back_populates="idol", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Idol(id={self.id}, name='{self.name}', is_active={self.is_active})>"
