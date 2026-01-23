"""
Pydantic schemas for conversations and messages
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Message Schemas
class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    sender_type: str = Field(..., pattern="^(user|idol)$", description="Sender type: user or idol")
    message_type: str = Field("text", pattern="^(text|voice|image|emoji)$", description="Message type")
    emotion: Optional[str] = Field(None, description="Emotion label")
    voice_url: Optional[str] = Field(None, description="Voice message URL")
    voice_duration: Optional[int] = Field(None, description="Voice duration in seconds")


class MessageResponse(MessageBase):
    """Message response schema"""
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Message timestamp")
    status: str = Field("sent", description="Message status")

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Request schema for creating a new conversation"""
    idol_id: int = Field(..., description="Idol ID to start conversation with")


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    idol_id: int = Field(..., description="Idol ID")
    intimacy_level: int = Field(1, description="Intimacy level (1-100)")
    intimacy_exp: int = Field(0, description="Intimacy experience points")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_message_at: datetime = Field(..., description="Last message timestamp")
    last_active_at: datetime = Field(..., description="Last active timestamp (heartbeat)")

    class Config:
        from_attributes = True


class ConversationWithWelcomeMessage(ConversationResponse):
    """Conversation response with initial welcome message"""
    welcome_message: MessageResponse = Field(..., description="Initial welcome message from idol")


class ConversationDetail(ConversationResponse):
    """Detailed conversation response with recent messages"""
    messages: List[MessageResponse] = Field(default_factory=list, description="Recent messages")


# Send Message Schema
class SendMessageRequest(BaseModel):
    """Request schema for sending a message"""
    content: str = Field(..., min_length=1, max_length=500, description="Message content (max 500 chars)")


class SendMessageResponse(BaseModel):
    """Response schema after sending a message"""
    user_message: MessageResponse = Field(..., description="User's sent message")
    idol_reply: Optional[MessageResponse] = Field(None, description="Idol's reply (will be implemented in Epic 2)")


# Emoji Message Schema
class SendEmojiRequest(BaseModel):
    """Request schema for sending an emoji message"""
    emoji: str = Field(..., min_length=1, max_length=10, description="Emoji character(s) to send")


# Message Status Update Schema
class MessageStatusUpdate(BaseModel):
    """Request schema for updating message status"""
    message_ids: List[int] = Field(..., description="List of message IDs to update")
    status: str = Field(..., pattern="^(read|delivered)$", description="New status")


class MessageStatusUpdateResponse(BaseModel):
    """Response schema after updating message status"""
    updated_count: int = Field(..., description="Number of messages updated")
    message: str = Field(..., description="Success message")


# Message History Schema
class MessageHistoryResponse(BaseModel):
    """Response schema for message history"""
    messages: List[MessageResponse] = Field(..., description="List of historical messages")
    has_more: bool = Field(..., description="Whether there are more messages to load")
    oldest_message_id: Optional[int] = Field(None, description="ID of the oldest message in this batch")


# Error Response
class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
