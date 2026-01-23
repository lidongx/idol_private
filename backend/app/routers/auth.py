"""
Authentication API Router
Handles user registration, login, and verification code sending
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    SendCodeRequest,
    SendCodeResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    UserResponse,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    CompleteOnboardingResponse,
    ErrorResponse
)
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.services import sms_service, auth_service
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/send-code",
    response_model=SendCodeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid phone number or rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="发送验证码",
    description="向手机号发送6位数字验证码，有效期5分钟"
)
async def send_verification_code(request: SendCodeRequest):
    """
    Send verification code to phone number

    - Validates phone number format
    - Checks rate limit (60s cooldown)
    - Generates and stores code in Redis
    - Sends SMS (MVP: console output)
    """
    # Check rate limit
    if not sms_service.can_resend_code(request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码发送过于频繁，请60秒后再试"
        )

    # Generate verification code
    code = sms_service.generate_verification_code()

    # Store in Redis
    if not sms_service.store_verification_code(request.phone, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码存储失败，请稍后重试"
        )

    # Send SMS
    if not sms_service.send_sms_code(request.phone, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败，请稍后重试"
        )

    # Set rate limit
    sms_service.set_resend_limit(request.phone)

    return SendCodeResponse(
        message="验证码已发送",
        expires_in=300
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Registration failed (invalid code, duplicate phone, etc.)"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="用户注册",
    description="使用手机号、验证码和密码注册新用户"
)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user

    - Validates phone, verification code, and password
    - Checks if phone already registered
    - Hashes password with bcrypt
    - Creates user record in database
    - Returns JWT access token
    """
    # Verify verification code
    if not sms_service.verify_verification_code(request.phone, request.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # Check if phone already registered
    existing_user = db.query(User).filter(User.phone == request.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册，请直接登录"
        )

    # Hash password
    password_hash = hash_password(request.password)

    # Create new user
    try:
        new_user = User(
            phone=request.phone,
            password_hash=password_hash,
            subscription_tier="free"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"user_id": new_user.id, "phone": new_user.phone}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Login failed (invalid credentials, account locked, etc.)"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="用户登录",
    description="使用手机号和密码登录，返回JWT Token和用户信息"
)
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login with phone and password

    - Validates phone and password
    - Checks account lock status (5 failed attempts = 30min lock)
    - Verifies credentials
    - Returns JWT token and user info
    - Clears failed attempts on success
    """
    # Check if account is locked
    if auth_service.check_account_locked(request.phone):
        lock_time = auth_service.get_lock_time_remaining(request.phone)
        minutes = lock_time // 60
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"账号已被锁定，请{minutes}分钟后再试"
        )

    # Find user by phone
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号未注册"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        # Increment failed login attempts
        attempts = auth_service.increment_login_attempts(request.phone)
        remaining = auth_service.get_remaining_attempts(request.phone)

        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码错误次数过多，账号已被锁定30分钟"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码错误，还有{remaining}次尝试机会"
            )

    # Clear failed login attempts on successful login
    auth_service.clear_login_attempts(request.phone)

    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "phone": user.phone,
            "subscription_tier": user.subscription_tier
        }
    )

    # Build user response
    user_response = UserResponse(
        id=user.id,
        phone=user.phone,
        subscription_tier=user.subscription_tier,
        onboarding_completed=user.onboarding_completed
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=604800,  # 7 days in seconds
        user=user_response
    )


@router.post(
    "/forgot-password",
    response_model=SendCodeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Phone not registered or rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="忘记密码（发送重置验证码）",
    description="向已注册的手机号发送密码重置验证码，有效期10分钟"
)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send password reset verification code

    - Validates phone number format
    - Checks if phone is registered
    - Checks rate limit (60s cooldown)
    - Generates and stores code in Redis with pwd:reset:{phone} key
    - Sends SMS (MVP: console output)
    """
    # Check if phone is registered
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号未注册，请先注册"
        )

    # Check rate limit
    if not sms_service.can_resend_code(request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码发送过于频繁，请60秒后再试"
        )

    # Generate verification code
    code = sms_service.generate_verification_code()

    # Store in Redis with pwd:reset:{phone} key (10 minutes TTL)
    if not sms_service.store_password_reset_code(request.phone, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码存储失败，请稍后重试"
        )

    # Send SMS
    if not sms_service.send_sms_code(request.phone, code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败，请稍后重试"
        )

    # Set rate limit
    sms_service.set_resend_limit(request.phone)

    return SendCodeResponse(
        message="重置密码验证码已发送",
        expires_in=600  # 10 minutes
    )


@router.post(
    "/reset-password",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid code or phone not registered"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="重置密码",
    description="使用验证码重置密码，成功后自动登录"
)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset user password with verification code

    - Validates phone, code, and new password
    - Checks if phone is registered
    - Verifies reset code from Redis (pwd:reset:{phone})
    - Updates password_hash in database
    - Auto-login: generates and returns JWT token
    """
    # Verify password reset code
    if not sms_service.verify_password_reset_code(request.phone, request.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # Find user by phone
    user = db.query(User).filter(User.phone == request.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号未注册"
        )

    # Hash new password
    new_password_hash = hash_password(request.new_password)

    # Update password in database
    try:
        user.password_hash = new_password_hash
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败，请稍后重试"
        )

    # Auto-login: Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "phone": user.phone,
            "subscription_tier": user.subscription_tier
        }
    )

    # Build user response
    user_response = UserResponse(
        id=user.id,
        phone=user.phone,
        subscription_tier=user.subscription_tier,
        onboarding_completed=user.onboarding_completed
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=604800,  # 7 days in seconds
        user=user_response
    )


@router.post(
    "/complete-onboarding",
    response_model=CompleteOnboardingResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="完成新手引导",
    description="标记用户已完成新手引导流程"
)
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark user's onboarding as completed

    - Requires JWT authentication
    - Updates onboarding_completed to True
    - Idempotent: safe to call multiple times
    """
    try:
        # Update onboarding status
        current_user.onboarding_completed = True
        db.commit()
        db.refresh(current_user)

        return CompleteOnboardingResponse(
            message="新手引导已完成",
            onboarding_completed=True
        )
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )
