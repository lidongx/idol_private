"""
Conversation API Router
Handles conversation creation and message management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationWithWelcomeMessage,
    ConversationResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    SendEmojiRequest,
    MessageStatusUpdate,
    MessageStatusUpdateResponse,
    MessageHistoryResponse,
    ErrorResponse
)
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.idol import Idol
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.welcome_service import get_welcome_message
from app.services.ai import AIProviderFactory
from app.services.cache_manager import cache_manager
from app.services.proactive_memory_service import ProactiveMemoryService
from app.services.emotion_analyzer import emotion_analyzer
from app.services.file_storage import file_storage
from app.services.quota_service import QuotaService
from app.services.memory_service import MemoryService
from app.services.reverse_care_service import ReverseCareService
from app.services.special_event_service import SpecialEventService
from app.services.intimacy_service import IntimacyService
from app.services.reward_service import RewardService
from app.services.achievement_service import AchievementService

router = APIRouter()


def _get_idol_emotion_response(user_emotion: str, confidence: float) -> str:
    """
    Determine idol's response emotion based on user's emotion

    Args:
        user_emotion: Detected user emotion
        confidence: Detection confidence

    Returns:
        Appropriate idol emotion for response
    """
    if confidence < 0.4:
        return "friendly"  # Default friendly tone

    # Map user emotion to appropriate idol response emotion
    emotion_mapping = {
        "happy": "happy",  # Share the joy
        "sad": "caring",  # Show care and comfort
        "angry": "calm",  # Stay calm and understanding
        "anxious": "reassuring",  # Provide reassurance
        "tired": "gentle",  # Be gentle and supportive
        "lonely": "warm",  # Warm companionship
        "excited": "excited",  # Match the excitement
        "neutral": "friendly"  # Default friendly
    }

    return emotion_mapping.get(user_emotion, "friendly")


@router.post(
    "/conversations",
    response_model=ConversationWithWelcomeMessage,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request (idol not found, etc.)"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        409: {"model": ErrorResponse, "description": "Conversation already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="创建新对话",
    description="创建用户与偶像的对话，并自动生成欢迎消息"
)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation between user and idol

    - Requires JWT authentication
    - Creates conversation record
    - Generates time-based welcome message from idol
    - Returns conversation with welcome message
    """
    # Verify idol exists
    idol = db.query(Idol).filter(Idol.id == request.idol_id, Idol.is_active == True).first()
    if not idol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="偶像不存在或已下线"
        )

    # Check if conversation already exists
    existing_conversation = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.idol_id == request.idol_id
    ).first()

    if existing_conversation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="与该偶像的对话已存在"
        )

    try:
        # Create new conversation
        new_conversation = Conversation(
            user_id=current_user.id,
            idol_id=request.idol_id,
            intimacy_level=1,
            intimacy_exp=0
        )
        db.add(new_conversation)
        db.flush()  # Get conversation ID before creating message

        # Generate welcome message based on time of day
        current_hour = datetime.now().hour
        welcome_text = get_welcome_message(current_hour)

        # Create welcome message
        welcome_message = Message(
            conversation_id=new_conversation.id,
            sender_type="idol",
            content=welcome_text,
            emotion="happy",
            status="delivered"
        )
        db.add(welcome_message)
        db.commit()
        db.refresh(new_conversation)
        db.refresh(welcome_message)

        # Build response
        return ConversationWithWelcomeMessage(
            id=new_conversation.id,
            user_id=new_conversation.user_id,
            idol_id=new_conversation.idol_id,
            intimacy_level=new_conversation.intimacy_level,
            intimacy_exp=new_conversation.intimacy_exp,
            created_at=new_conversation.created_at,
            last_message_at=new_conversation.last_message_at,
            welcome_message=MessageResponse(
                id=welcome_message.id,
                conversation_id=welcome_message.conversation_id,
                sender_type=welcome_message.sender_type,
                content=welcome_message.content,
                emotion=welcome_message.emotion,
                timestamp=welcome_message.timestamp,
                status=welcome_message.status
            )
        )

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话失败，请稍后重试"
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="获取对话详情",
    description="获取指定对话的基本信息"
)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation details

    - Requires JWT authentication
    - Returns conversation basic info
    - Validates user owns the conversation
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        idol_id=conversation.idol_id,
        intimacy_level=conversation.intimacy_level,
        intimacy_exp=conversation.intimacy_exp,
        created_at=conversation.created_at,
        last_message_at=conversation.last_message_at
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="发送消息",
    description="用户发送消息并接收AI偶像的回复"
)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message and get AI response

    - Requires JWT authentication
    - Validates user owns the conversation
    - Saves user message to database
    - Generates AI response using configured provider
    - Saves AI response to database
    - Returns both messages
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Check and increment message quota (Story 3.1)
        quota_service = QuotaService(db)
        quota = quota_service.check_and_increment_quota(current_user.id)
        print(f"[Quota] User {current_user.id} - {quota.messages_sent}/{quota.quota_limit}")

        # Detect user emotion from message
        user_emotion, emotion_confidence = emotion_analyzer.detect_emotion(
            request.content,
            use_ai=False  # Use keyword-based for speed (MVP)
        )
        print(f"[Emotion] Detected: {user_emotion} (confidence: {emotion_confidence:.2f})")

        # Save user message with emotion
        user_message = Message(
            conversation_id=conversation_id,
            sender_type="user",
            content=request.content,
            emotion=user_emotion if emotion_confidence >= 0.4 else None,
            status="sent"
        )
        db.add(user_message)
        db.flush()

        # Story 5.4: Update user's last_active_at timestamp
        current_user.last_active_at = datetime.utcnow()

        # Story 5.4: Check for late night activity (1:00-3:00 AM)
        reverse_care_context = ""
        reverse_care_service = ReverseCareService(db)
        if reverse_care_service.check_late_night_activity(current_user.id):
            # Send late night care message
            care_result = reverse_care_service.send_late_night_care_message(
                user_id=current_user.id,
                idol_id=conversation.idol_id
            )
            # Inject care message into the conversation flow
            reverse_care_context = f"\n\n【深夜关心】\n先关心一下用户这么晚还不睡：\n\"{care_result['message']}\"\n\n然后再回复用户的消息。"
            print(f"[Reverse Care] Late night care triggered: {care_result['message'][:50]}...")

        # Get idol information for personality prompt
        idol = db.query(Idol).filter(Idol.id == conversation.idol_id).first()
        if not idol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="偶像不存在"
            )

        # L1 Cache: Try to get conversation context from cache
        cached_context = cache_manager.get_conversation_context(conversation_id)

        if cached_context:
            print(f"[Cache] L1 HIT: conversation_id={conversation_id}")
            # Convert cached context back to message-like dicts
            recent_messages_data = cached_context
        else:
            print(f"[Cache] L1 MISS: conversation_id={conversation_id}")
            # Load recent conversation history from database (last 10 messages)
            recent_messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.desc()).limit(10).all()

            # Reverse to chronological order
            recent_messages.reverse()

            # Convert to serializable format for caching
            recent_messages_data = [
                {
                    "sender_type": msg.sender_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in recent_messages
            ]

            # Store in L1 cache (15 min TTL)
            cache_manager.set_conversation_context(conversation_id, recent_messages_data)

        # Story 4.3: Recall relevant memories using semantic search
        memory_service = MemoryService(db)
        relevant_memories = await memory_service.search_memories(
            user_id=current_user.id,
            query=request.content,
            limit=3,
        )

        # Build memory context string
        memory_context = ""
        if relevant_memories:
            memory_lines = []
            for mem_result in relevant_memories:
                memory = mem_result['memory']
                similarity = mem_result['similarity']
                # Only include memories with similarity > 0.5 (50%)
                if similarity >= 0.5:
                    memory_lines.append(f"- {memory.content}")
                    # Mark memory as mentioned
                    memory_service.mark_memory_mentioned(memory.id)

            if memory_lines:
                memory_context = "\n\n关于用户的记忆：\n" + "\n".join(memory_lines)
                print(f"[Memory] Recalled {len(memory_lines)} relevant memories")

        # Story 4.6: Check for proactive mention opportunity
        proactive_context = ""
        proactive_memory_service = ProactiveMemoryService(db)
        proactive_mention_info = await proactive_memory_service.check_and_send_proactive_mention(current_user.id)

        if proactive_mention_info:
            # Record the proactive mention
            proactive_mention = proactive_memory_service.record_proactive_mention(
                user_id=current_user.id,
                memory_id=proactive_mention_info['memory_id'],
                proactive_message=proactive_mention_info['proactive_message']
            )

            # Add proactive instruction to prompt
            proactive_context = f"\n\n【主动关心指令】\n在回复用户之前，先主动关心一下这件事：\n\"{proactive_mention_info['proactive_message']}\"\n\n然后再自然地回复用户的消息。两个话题要衔接得自然。"
            print(f"[Proactive] Mentioning memory {proactive_mention_info['memory_id']}: {proactive_mention_info['proactive_message'][:50]}...")

        # Story 5.5: Check for special events
        special_event_context = ""
        special_event_service = SpecialEventService(db)
        triggered_event = special_event_service.check_all_events(current_user.id, conversation.idol_id)

        if triggered_event:
            # Inject special event into conversation
            special_event_context = f"\n\n【特殊事件】\n你想分享一件事：\n\"{triggered_event['content']}\"\n\n自然地融入到对话中分享给用户。"
            print(f"[Special Event] Triggered: {triggered_event['event_name']} - {triggered_event['event_type']}")

        # Story 6.1: Add intimacy exp for sending message
        intimacy_context = ""
        intimacy_service = IntimacyService(db)
        intimacy_result = intimacy_service.add_message_exp(conversation_id)

        if intimacy_result['level_up']:
            # Level up! Inject celebration context
            old_level = intimacy_result['old_level']
            new_level = intimacy_result['new_level']
            level_title = intimacy_service.get_level_title(new_level)
            intimacy_context = f"\n\n【亲密度升级】\n你们的关系刚刚升级了！从等级 {old_level} 升到了等级 {new_level}（{level_title}）！\n请自然地表达你的喜悦，庆祝这个特殊时刻。"
            print(f"[Intimacy] Level up! {old_level} -> {new_level} ({level_title})")
        else:
            print(f"[Intimacy] +{intimacy_result['exp_added']} exp (Level {intimacy_result['new_level']}, {intimacy_result['new_exp']}/{intimacy_result['required_exp_for_next']})")

        # Story 6.3: Check for active nickname reward
        nickname_context = ""
        reward_service = RewardService(db)
        active_nickname = reward_service.get_active_nickname(current_user.id)
        if active_nickname:
            nickname_context = f"\n\n【专属昵称】\n你已经解锁了专属昵称，请在对话中称呼用户为「{active_nickname}」。"
            print(f"[Reward] Active nickname: {active_nickname}")

        # Story 6.4: Check for achievement unlocks
        achievement_service = AchievementService(db)
        newly_unlocked_achievements = achievement_service.check_message_achievements(current_user.id)

        if newly_unlocked_achievements:
            print(f"[Achievement] Unlocked {len(newly_unlocked_achievements)} achievements:")
            for ua in newly_unlocked_achievements:
                print(f"  - {ua.achievement.achievement_name} (+{ua.achievement.reward_exp} exp)")
                # Add exp reward from achievement to intimacy
                ach_exp_result = intimacy_service.add_intimacy_exp(
                    conversation_id,
                    ua.achievement.reward_exp,
                    f"achievement_{ua.achievement_id}"
                )
                # Check if this additional exp caused a level up
                if ach_exp_result['level_up']:
                    print(f"[Achievement] Bonus level up from achievement reward!")

        # Build AI prompt
        messages = []

        # Enhance system prompt with emotion-aware strategy
        enhanced_prompt = emotion_analyzer.enhance_prompt_with_emotion(
            base_prompt=idol.personality_prompt,
            emotion=user_emotion,
            confidence=emotion_confidence
        )

        # Inject memory context, proactive context, reverse care context, special event context, intimacy context, and nickname context into system prompt
        enhanced_prompt_with_memory = enhanced_prompt + memory_context + proactive_context + reverse_care_context + special_event_context + intimacy_context + nickname_context

        # System prompt with idol personality + emotion guidance + memory context + proactive instruction + reverse care + special events + nickname
        messages.append({
            "role": "system",
            "content": enhanced_prompt_with_memory
        })

        # Add conversation history (exclude the message we just added)
        for msg_data in recent_messages_data[:-1]:
            if msg_data["sender_type"] == "user":
                messages.append({"role": "user", "content": msg_data["content"]})
            elif msg_data["sender_type"] == "idol":
                messages.append({"role": "assistant", "content": msg_data["content"]})

        # Add current user message
        messages.append({"role": "user", "content": request.content})

        # L2 Cache: Try to get common response from cache
        cached_response = cache_manager.get_common_response(request.content)

        if cached_response:
            print(f"[Cache] L2 HIT: question_hash={request.content[:30]}...")
            ai_response = cached_response
        else:
            print(f"[Cache] L2 MISS: question={request.content[:30]}...")
            # Generate AI response
            ai_provider = AIProviderFactory.get_provider()
            ai_response = await ai_provider.generate_response(
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )

            # Store in L2 cache (24 hour TTL)
            cache_manager.set_common_response(request.content, ai_response)

        # Determine idol response emotion based on user emotion
        idol_emotion = _get_idol_emotion_response(user_emotion, emotion_confidence)

        # Save AI response with emotion
        idol_message = Message(
            conversation_id=conversation_id,
            sender_type="idol",
            content=ai_response,
            emotion=idol_emotion,
            status="delivered"
        )
        db.add(idol_message)

        # Update conversation last_message_at
        conversation.last_message_at = datetime.now()

        db.commit()
        db.refresh(user_message)
        db.refresh(idol_message)

        # Invalidate L1 cache since we have new messages
        cache_manager.invalidate_conversation_context(conversation_id)
        print(f"[Cache] L1 INVALIDATED: conversation_id={conversation_id}")

        # Story 8.2: Broadcast messages to all user's devices via SSE
        from app.services.message_broadcast_service import MessageBroadcastService
        broadcast_service = MessageBroadcastService()

        # Broadcast user message
        user_subscribers = broadcast_service.broadcast_new_message(
            user_id=current_user.id,
            message_id=user_message.id,
            conversation_id=conversation_id,
            content=user_message.content,
            sender_type="user",
            created_at=user_message.timestamp.isoformat()
        )

        # Broadcast idol message
        idol_subscribers = broadcast_service.broadcast_new_message(
            user_id=current_user.id,
            message_id=idol_message.id,
            conversation_id=conversation_id,
            content=idol_message.content,
            sender_type="idol",
            created_at=idol_message.timestamp.isoformat()
        )

        print(f"[SSE] Broadcast to {max(user_subscribers, idol_subscribers)} devices")

        # Build response
        return SendMessageResponse(
            user_message=MessageResponse(
                id=user_message.id,
                conversation_id=user_message.conversation_id,
                sender_type=user_message.sender_type,
                content=user_message.content,
                emotion=user_message.emotion,
                timestamp=user_message.timestamp,
                status=user_message.status
            ),
            idol_reply=MessageResponse(
                id=idol_message.id,
                conversation_id=idol_message.conversation_id,
                sender_type=idol_message.sender_type,
                content=idol_message.content,
                emotion=idol_message.emotion,
                timestamp=idol_message.timestamp,
                status=idol_message.status
            )
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Message send error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"消息发送失败: {str(e)}"
        )


@router.put(
    "/conversations/{conversation_id}/messages/status",
    response_model=MessageStatusUpdateResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="更新消息状态",
    description="批量更新消息状态（标记为已读/已送达）"
)
async def update_message_status(
    conversation_id: int,
    request: MessageStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update message status (mark as read/delivered)

    - Requires JWT authentication
    - Can only update messages in user's own conversations
    - Batch update multiple messages at once
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Update message status
        updated_count = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.id.in_(request.message_ids),
            Message.sender_type == "idol"  # Only update idol messages
        ).update(
            {"status": request.status},
            synchronize_session=False
        )

        db.commit()

        return MessageStatusUpdateResponse(
            updated_count=updated_count,
            message=f"成功更新 {updated_count} 条消息状态为 {request.status}"
        )

    except Exception as e:
        db.rollback()
        print(f"Message status update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新消息状态失败"
        )


@router.post(
    "/conversations/{conversation_id}/messages/voice",
    response_model=SendMessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        413: {"model": ErrorResponse, "description": "File too large"},
    },
    summary="发送语音消息",
    description="上传并发送语音消息，AI会生成文本回复"
)
async def send_voice_message(
    conversation_id: int,
    voice_file: UploadFile = File(..., description="Voice audio file (MP3/M4A/WAV)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send voice message

    - Requires JWT authentication
    - Uploads voice file to server
    - Creates voice message in database
    - Returns voice message (AI text reply will come in future iteration)
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Save voice file
        voice_url, duration = await file_storage.save_voice_file(
            file=voice_file,
            user_id=current_user.id
        )

        # Create voice message
        user_message = Message(
            conversation_id=conversation_id,
            sender_type="user",
            message_type="voice",
            content="[语音消息]",  # Placeholder text
            voice_url=voice_url,
            voice_duration=duration,
            status="sent"
        )
        db.add(user_message)
        db.flush()

        # Story 6.1: Add intimacy exp for sending voice message
        intimacy_service = IntimacyService(db)
        intimacy_result = intimacy_service.add_voice_exp(conversation_id)
        print(f"[Intimacy] Voice +{intimacy_result['exp_added']} exp (Level {intimacy_result['new_level']})")

        # Get idol for personality
        idol = db.query(Idol).filter(Idol.id == conversation.idol_id).first()

        # For MVP: Generate text reply (no voice-to-text needed)
        # AI will respond with text to voice message
        messages = [
            {"role": "system", "content": idol.personality_prompt},
            {"role": "user", "content": "用户发送了一条语音消息"}
        ]

        ai_provider = AIProviderFactory.get_provider()
        ai_response = await ai_provider.generate_response(
            messages=messages,
            temperature=0.8,
            max_tokens=200
        )

        # Save AI text reply
        idol_message = Message(
            conversation_id=conversation_id,
            sender_type="idol",
            message_type="text",
            content=ai_response,
            emotion="friendly",
            status="delivered"
        )
        db.add(idol_message)

        # Update conversation timestamp
        conversation.last_message_at = datetime.now()
        db.commit()
        db.refresh(user_message)
        db.refresh(idol_message)

        return SendMessageResponse(
            user_message=MessageResponse(
                id=user_message.id,
                conversation_id=user_message.conversation_id,
                sender_type=user_message.sender_type,
                message_type=user_message.message_type,
                content=user_message.content,
                voice_url=user_message.voice_url,
                voice_duration=user_message.voice_duration,
                emotion=user_message.emotion,
                timestamp=user_message.timestamp,
                status=user_message.status
            ),
            idol_reply=MessageResponse(
                id=idol_message.id,
                conversation_id=idol_message.conversation_id,
                sender_type=idol_message.sender_type,
                message_type=idol_message.message_type,
                content=idol_message.content,
                voice_url=idol_message.voice_url,
                voice_duration=idol_message.voice_duration,
                emotion=idol_message.emotion,
                timestamp=idol_message.timestamp,
                status=idol_message.status
            )
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Voice message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音消息发送失败: {str(e)}"
        )


@router.post(
    "/conversations/{conversation_id}/messages/image",
    response_model=SendMessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
        413: {"model": ErrorResponse, "description": "File too large"},
    },
    summary="发送图片消息",
    description="上传并发送图片消息，AI会识别图片内容并回复"
)
async def send_image_message(
    conversation_id: int,
    image_file: UploadFile = File(..., description="Image file (JPG/PNG/GIF/WEBP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send image message

    - Requires JWT authentication
    - Uploads image file to server
    - Creates image message in database
    - AI generates text reply (MVP: generic response, no image recognition)
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Save image file
        image_url = await file_storage.save_image_file(
            file=image_file,
            user_id=current_user.id
        )

        # Create image message
        user_message = Message(
            conversation_id=conversation_id,
            sender_type="user",
            message_type="image",
            content="[图片]",  # Placeholder text
            voice_url=image_url,  # Reuse voice_url for image URL (MVP)
            status="sent"
        )
        db.add(user_message)
        db.flush()

        # Story 6.1: Add intimacy exp for sending image message
        intimacy_service = IntimacyService(db)
        intimacy_result = intimacy_service.add_image_exp(conversation_id)
        print(f"[Intimacy] Image +{intimacy_result['exp_added']} exp (Level {intimacy_result['new_level']})")

        # Get idol for personality
        idol = db.query(Idol).filter(Idol.id == conversation.idol_id).first()

        # For MVP: Generate generic text reply (no image recognition)
        # Future: Use Vision API to recognize image content
        messages = [
            {"role": "system", "content": idol.personality_prompt},
            {"role": "user", "content": "用户发送了一张图片"}
        ]

        ai_provider = AIProviderFactory.get_provider()
        ai_response = await ai_provider.generate_response(
            messages=messages,
            temperature=0.8,
            max_tokens=200
        )

        # Save AI text reply
        idol_message = Message(
            conversation_id=conversation_id,
            sender_type="idol",
            message_type="text",
            content=ai_response,
            emotion="friendly",
            status="delivered"
        )
        db.add(idol_message)

        # Update conversation timestamp
        conversation.last_message_at = datetime.now()
        db.commit()
        db.refresh(user_message)
        db.refresh(idol_message)

        return SendMessageResponse(
            user_message=MessageResponse(
                id=user_message.id,
                conversation_id=user_message.conversation_id,
                sender_type=user_message.sender_type,
                message_type=user_message.message_type,
                content=user_message.content,
                voice_url=user_message.voice_url,
                voice_duration=user_message.voice_duration,
                emotion=user_message.emotion,
                timestamp=user_message.timestamp,
                status=user_message.status
            ),
            idol_reply=MessageResponse(
                id=idol_message.id,
                conversation_id=idol_message.conversation_id,
                sender_type=idol_message.sender_type,
                message_type=idol_message.message_type,
                content=idol_message.content,
                voice_url=idol_message.voice_url,
                voice_duration=idol_message.voice_duration,
                emotion=idol_message.emotion,
                timestamp=idol_message.timestamp,
                status=idol_message.status
            )
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Image message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片消息发送失败: {str(e)}"
        )


@router.post(
    "/conversations/{conversation_id}/messages/emoji",
    response_model=SendMessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="发送表情消息",
    description="发送emoji表情消息，AI会根据表情回复"
)
async def send_emoji_message(
    conversation_id: int,
    request: SendEmojiRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send emoji message

    - Requires JWT authentication
    - Sends emoji as message content
    - AI generates contextual reply based on emoji sentiment
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Create emoji message
        user_message = Message(
            conversation_id=conversation_id,
            sender_type="user",
            message_type="emoji",
            content=request.emoji,
            status="sent"
        )
        db.add(user_message)
        db.flush()

        # Get idol for personality
        idol = db.query(Idol).filter(Idol.id == conversation.idol_id).first()

        # Detect emoji sentiment for contextual reply
        emoji_sentiment_map = {
            # Happy/Love emojis
            "😊": "happy", "😄": "happy", "🥰": "loving", "❤️": "loving", "💕": "loving",
            "😍": "loving", "🤗": "warm", "😘": "affectionate", "💖": "loving",
            # Sad/Worried emojis
            "😢": "sad", "😭": "very_sad", "😔": "disappointed", "😟": "worried",
            "😞": "sad", "🥺": "pleading", "😿": "sad",
            # Angry/Frustrated emojis
            "😠": "angry", "😡": "very_angry", "💢": "frustrated", "😤": "annoyed",
            # Excited/Playful emojis
            "🎉": "excited", "🎊": "celebratory", "✨": "excited", "🤩": "amazed",
            "😆": "laughing", "🤣": "hilarious", "😂": "laughing",
            # Tired/Sleepy emojis
            "😴": "sleepy", "🥱": "tired", "😪": "tired",
            # Thinking/Neutral emojis
            "🤔": "thinking", "😐": "neutral", "😶": "speechless",
            # Greeting/Waving emojis
            "👋": "greeting", "👏": "applauding", "🙌": "celebrating",
        }

        emoji_sentiment = emoji_sentiment_map.get(request.emoji, "friendly")

        # Generate context-aware prompt based on emoji
        emoji_context = f"用户发送了表情 {request.emoji}"
        if emoji_sentiment in ["happy", "loving", "affectionate"]:
            emoji_context += "，请用亲切温暖的语气回复"
        elif emoji_sentiment in ["sad", "very_sad", "disappointed"]:
            emoji_context += "，请用关心体贴的语气安慰用户"
        elif emoji_sentiment in ["excited", "celebratory", "amazed"]:
            emoji_context += "，请用同样兴奋的语气回复"
        elif emoji_sentiment in ["tired", "sleepy"]:
            emoji_context += "，请用轻柔关怀的语气回复"

        # Generate AI reply
        messages = [
            {"role": "system", "content": idol.personality_prompt},
            {"role": "user", "content": emoji_context}
        ]

        ai_provider = AIProviderFactory.get_provider()
        ai_response = await ai_provider.generate_response(
            messages=messages,
            temperature=0.8,
            max_tokens=150
        )

        # Map emoji sentiment to idol emotion
        idol_emotion_map = {
            "happy": "happy",
            "loving": "loving",
            "affectionate": "warm",
            "sad": "caring",
            "very_sad": "caring",
            "disappointed": "comforting",
            "worried": "reassuring",
            "excited": "excited",
            "celebratory": "excited",
            "amazed": "enthusiastic",
            "tired": "gentle",
            "sleepy": "gentle",
            "friendly": "friendly",
        }
        idol_emotion = idol_emotion_map.get(emoji_sentiment, "friendly")

        # Save AI reply
        idol_message = Message(
            conversation_id=conversation_id,
            sender_type="idol",
            message_type="text",
            content=ai_response,
            emotion=idol_emotion,
            status="delivered"
        )
        db.add(idol_message)

        # Update conversation timestamp
        conversation.last_message_at = datetime.now()
        db.commit()
        db.refresh(user_message)
        db.refresh(idol_message)

        return SendMessageResponse(
            user_message=MessageResponse(
                id=user_message.id,
                conversation_id=user_message.conversation_id,
                sender_type=user_message.sender_type,
                message_type=user_message.message_type,
                content=user_message.content,
                emotion=user_message.emotion,
                timestamp=user_message.timestamp,
                status=user_message.status
            ),
            idol_reply=MessageResponse(
                id=idol_message.id,
                conversation_id=idol_message.conversation_id,
                sender_type=idol_message.sender_type,
                message_type=idol_message.message_type,
                content=idol_message.content,
                emotion=idol_message.emotion,
                timestamp=idol_message.timestamp,
                status=idol_message.status
            )
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Emoji message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"表情消息发送失败: {str(e)}"
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageHistoryResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="获取历史消息",
    description="分页获取对话历史消息，支持无限向上滚动加载"
)
async def get_message_history(
    conversation_id: int,
    before: int = None,  # Message ID to load messages before (for pagination)
    limit: int = 20,  # Number of messages per page
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get message history with pagination

    - Requires JWT authentication
    - Returns messages in reverse chronological order (newest first)
    - Use 'before' parameter for pagination (load older messages)
    - Limit default is 20, max is 100

    Example usage:
    - First load: GET /conversations/1/messages?limit=20
    - Load more: GET /conversations/1/messages?before=123&limit=20
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    # Limit max page size
    limit = min(limit, 100)

    try:
        # Build query
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.id.desc())  # Newest first

        # Apply pagination
        if before:
            query = query.filter(Message.id < before)

        # Fetch messages
        messages = query.limit(limit + 1).all()  # Fetch one extra to check if has_more

        # Check if there are more messages
        has_more = len(messages) > limit
        if has_more:
            messages = messages[:limit]  # Remove the extra message

        # Get oldest message ID for next pagination
        oldest_message_id = messages[-1].id if messages else None

        # Convert to response format
        message_responses = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_type=msg.sender_type,
                message_type=msg.message_type,
                content=msg.content,
                voice_url=msg.voice_url,
                voice_duration=msg.voice_duration,
                emotion=msg.emotion,
                timestamp=msg.timestamp,
                status=msg.status
            )
            for msg in messages
        ]

        return MessageHistoryResponse(
            messages=message_responses,
            has_more=has_more,
            oldest_message_id=oldest_message_id
        )

    except Exception as e:
        print(f"Message history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取历史消息失败"
        )


@router.post(
    "/conversations/{conversation_id}/heartbeat",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="发送心跳信号",
    description="更新用户活跃时间，用于空闲状态检测"
)
async def send_heartbeat(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send heartbeat to update last active time

    - Requires JWT authentication
    - Updates last_active_at timestamp
    - Should be called every 30 seconds when user is active
    - Used for idle status detection (30s/60s prompts)
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Update last_active_at
        conversation.last_active_at = datetime.now()
        db.commit()

        return {
            "message": "心跳已更新",
            "last_active_at": conversation.last_active_at
        }

    except Exception as e:
        db.rollback()
        print(f"Heartbeat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="心跳更新失败"
        )


@router.post(
    "/conversations/{conversation_id}/idle-prompt",
    response_model=MessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    summary="触发空闲提示消息",
    description="60秒空闲后偶像主动发送提示消息"
)
async def send_idle_prompt(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send idle prompt message from idol

    - Requires JWT authentication
    - Creates an idol message: "还在吗？~"
    - Should only be called once per idle session
    - Frontend responsibility to track if prompt already sent
    """
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )

    try:
        # Create idle prompt message from idol
        idle_message = Message(
            conversation_id=conversation_id,
            sender_type="idol",
            message_type="text",
            content="还在吗？~",
            emotion="curious",
            status="delivered"
        )
        db.add(idle_message)

        # Update conversation timestamp
        conversation.last_message_at = datetime.now()
        db.commit()
        db.refresh(idle_message)

        return MessageResponse(
            id=idle_message.id,
            conversation_id=idle_message.conversation_id,
            sender_type=idle_message.sender_type,
            message_type=idle_message.message_type,
            content=idle_message.content,
            emotion=idle_message.emotion,
            timestamp=idle_message.timestamp,
            status=idle_message.status
        )

    except Exception as e:
        db.rollback()
        print(f"Idle prompt error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="空闲提示发送失败"
        )


@router.get(
    "/cache/health",
    summary="缓存健康检查",
    description="检查Redis缓存状态和统计信息"
)
async def cache_health_check():
    """
    Check cache health and get statistics

    - Returns cache connection status
    - Returns cache hit/miss statistics
    - Returns memory usage information
    """
    try:
        is_healthy = cache_manager.health_check()
        stats = cache_manager.get_cache_stats()

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "redis_connected": is_healthy,
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis_connected": False,
            "error": str(e)
        }
