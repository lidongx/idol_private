"""
Pydantic schemas for message quotas
"""
from pydantic import BaseModel, Field
from datetime import date


class QuotaResponse(BaseModel):
    """Response schema for user quota information"""
    date: str = Field(..., description="Quota date (YYYY-MM-DD)")
    messages_sent: int = Field(..., description="Messages sent today")
    quota_limit: int = Field(..., description="Daily quota limit (-1 for unlimited)")
    remaining: int = Field(..., description="Remaining messages (-1 for unlimited)")
    is_unlimited: bool = Field(..., description="Whether user has unlimited quota")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-01-14",
                "messages_sent": 5,
                "quota_limit": 20,
                "remaining": 15,
                "is_unlimited": False
            }
        }
