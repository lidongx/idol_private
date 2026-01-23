"""
Server-Sent Events (SSE) API router
Story 8.2: 实时消息同步（SSE）
"""
import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.redis_client import get_redis_pubsub
from app.services.message_broadcast_service import MessageBroadcastService


router = APIRouter(prefix="/sse", tags=["sse"])


async def message_stream_generator(user_id: int, request: Request) -> AsyncGenerator[str, None]:
    """
    Generate SSE stream for user's messages

    Args:
        user_id: User ID
        request: FastAPI request object (to detect client disconnect)

    Yields:
        str: SSE formatted message
    """
    # Create a new pub/sub instance for this connection
    pubsub = get_redis_pubsub()

    # Get user's message channel
    broadcast_service = MessageBroadcastService()
    channel = broadcast_service.get_user_channel(user_id)

    try:
        # Subscribe to user's message channel
        pubsub.subscribe(channel)

        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'user_id': user_id})}\n\n"

        # Listen for messages
        while True:
            # Check if client is still connected
            if await request.is_disconnected():
                break

            # Get message from Redis (non-blocking with timeout)
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

            if message and message['type'] == 'message':
                # Forward message to client in SSE format
                data = message['data']
                yield f"data: {data}\n\n"

            # Small delay to prevent busy loop
            await asyncio.sleep(0.1)

    finally:
        # Clean up subscription
        pubsub.unsubscribe(channel)
        pubsub.close()


@router.get(
    "/messages",
    summary="消息流订阅",
    description="订阅用户消息流，接收实时消息推送"
)
async def subscribe_message_stream(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to user's message stream via Server-Sent Events

    Returns:
        StreamingResponse: SSE stream with real-time messages

    Events:
    - connected: Initial connection established
    - new_message: New message received
    - typing_indicator: Someone is typing
    - message_status: Message status changed

    Example client code (JavaScript):
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/messages');

    eventSource.addEventListener('connected', (e) => {
        console.log('Connected:', JSON.parse(e.data));
    });

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.event === 'new_message') {
            // Handle new message
        }
    };
    ```
    """
    return StreamingResponse(
        message_stream_generator(current_user.id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get(
    "/heartbeat",
    summary="心跳检测",
    description="测试SSE连接是否正常"
)
async def sse_heartbeat(
    current_user: User = Depends(get_current_user)
):
    """
    Heartbeat endpoint to test SSE connectivity

    Returns:
        dict: Status message
    """
    return {
        "status": "ok",
        "user_id": current_user.id,
        "message": "SSE service is available"
    }
