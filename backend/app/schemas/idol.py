"""
Pydantic schemas for idol endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IdolBase(BaseModel):
    """Base idol schema"""
    name: str = Field(..., description="Idol name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    description: Optional[str] = Field(None, description="Short description")
    hobbies: Optional[str] = Field(None, description="Comma-separated hobbies")
    background_story: Optional[str] = Field(None, description="Background story")


class IdolResponse(IdolBase):
    """
    Idol response schema for API endpoints

    Note: personality_prompt is excluded from public API for security
    """
    id: int = Field(..., description="Idol ID")
    is_active: bool = Field(..., description="Whether idol is active")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class IdolListItem(BaseModel):
    """
    Simplified idol schema for list endpoints

    Returns only essential information for idol selection
    """
    id: int = Field(..., description="Idol ID")
    name: str = Field(..., description="Idol name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    description: Optional[str] = Field(None, description="Short description")
    hobbies_list: List[str] = Field(default_factory=list, description="List of hobbies")

    class Config:
        from_attributes = True


class IdolListResponse(BaseModel):
    """Response schema for GET /api/v1/idols"""
    idols: List[IdolListItem] = Field(..., description="List of active idols")


class IdolDetailResponse(BaseModel):
    """Response schema for GET /api/v1/idols/{idol_id}"""
    idol: IdolResponse = Field(..., description="Idol details")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
