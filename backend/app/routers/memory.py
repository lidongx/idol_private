"""
Memory API Router
Handles memory queries and extraction
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.memory_service import MemoryService
from app.services.memory_extraction_service import MemoryExtractionService
from pydantic import BaseModel


router = APIRouter()


# ========== Schemas ==========

class MemoryResponse(BaseModel):
    """Memory response schema"""
    id: int
    content: str
    memory_type: Optional[str]
    importance: str
    created_at: str
    last_mentioned_at: Optional[str]

    class Config:
        from_attributes = True


class ExtractMemoriesRequest(BaseModel):
    """Extract memories request"""
    conversation_id: int


class ExtractMemoriesResponse(BaseModel):
    """Extract memories response"""
    conversation_id: int
    extracted_count: int
    memories: List[dict]


class TagResponse(BaseModel):
    """Tag response schema"""
    tag_name: str
    tag_value: str


# ========== Endpoints ==========

@router.get(
    "/users/me/memories",
    response_model=List[MemoryResponse],
    summary="获取用户记忆",
    description="获取当前用户的所有记忆"
)
async def get_my_memories(
    memory_type: Optional[str] = None,
    importance: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's memories

    Optional filters:
    - memory_type: hobby, work, family, feeling, goal, preference, event
    - importance: low, medium, high
    - limit: Maximum results (default: 10)
    """
    memory_service = MemoryService(db)

    memories = memory_service.get_user_memories(
        user_id=current_user.id,
        memory_type=memory_type,
        importance=importance,
        limit=limit,
    )

    return [
        MemoryResponse(
            id=m.id,
            content=m.content,
            memory_type=m.memory_type,
            importance=m.importance,
            created_at=m.created_at.isoformat(),
            last_mentioned_at=m.last_mentioned_at.isoformat() if m.last_mentioned_at else None,
        )
        for m in memories
    ]


@router.post(
    "/conversations/{conversation_id}/extract-memories",
    response_model=ExtractMemoriesResponse,
    summary="手动提取记忆",
    description="从指定对话中提取记忆（用于测试和调试）"
)
async def extract_memories(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger memory extraction from a conversation

    This endpoint is useful for testing and debugging.
    In production, memories are extracted automatically by background task.
    """
    extraction_service = MemoryExtractionService(db)

    try:
        memories = await extraction_service.extract_memories_from_conversation(
            conversation_id=conversation_id,
            message_limit=20,
        )

        return ExtractMemoriesResponse(
            conversation_id=conversation_id,
            extracted_count=len(memories),
            memories=memories,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get(
    "/users/me/tags",
    response_model=dict,
    summary="获取用户标签",
    description="获取用户的所有属性标签"
)
async def get_my_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all user tags

    Returns dictionary of tag_name -> tag_value
    """
    memory_service = MemoryService(db)
    tags = memory_service.get_all_tags(user_id=current_user.id)

    return tags


@router.delete(
    "/users/me/memories/{memory_id}",
    summary="删除记忆",
    description="删除指定记忆"
)
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a memory

    Returns:
        Success message
    """
    memory_service = MemoryService(db)

    success = memory_service.delete_memory(
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")

    return {"message": "Memory deleted successfully"}
