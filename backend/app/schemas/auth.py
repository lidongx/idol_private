"""
Pydantic schemas for authentication endpoints
"""
from pydantic import BaseModel, Field, field_validator
import re


class SendCodeRequest(BaseModel):
    """Request schema for sending verification code"""
    phone: str = Field(..., description="11-digit Chinese phone number")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误，请输入11位有效手机号')
        return v


class SendCodeResponse(BaseModel):
    """Response schema for send code endpoint"""
    message: str = Field(..., description="Success message")
    expires_in: int = Field(300, description="Code expiration time in seconds")


class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    phone: str = Field(..., description="11-digit Chinese phone number")
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    password: str = Field(..., min_length=8, description="Password (at least 8 characters)")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误')
        return v

    @field_validator('verification_code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate verification code format"""
        if not v.isdigit():
            raise ValueError('验证码必须是6位数字')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('密码至少8位')
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class LoginRequest(BaseModel):
    """Request schema for user login"""
    phone: str = Field(..., description="11-digit Chinese phone number")
    password: str = Field(..., description="User password")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误')
        return v


class UserResponse(BaseModel):
    """User information response schema"""
    id: int = Field(..., description="User ID")
    phone: str = Field(..., description="Phone number")
    subscription_tier: str = Field(..., description="Subscription tier (free/basic/premium)")
    onboarding_completed: bool = Field(False, description="Whether user has completed onboarding")


class TokenResponse(BaseModel):
    """Response schema for successful authentication"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class LoginResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(604800, description="Token expiration time in seconds (7 days)")
    user: UserResponse = Field(..., description="User information")


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password (send reset code)"""
    phone: str = Field(..., description="11-digit Chinese phone number")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误')
        return v


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset"""
    phone: str = Field(..., description="11-digit Chinese phone number")
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    new_password: str = Field(..., min_length=8, description="New password (at least 8 characters)")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式错误')
        return v

    @field_validator('verification_code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate verification code format"""
        if not v.isdigit():
            raise ValueError('验证码必须是6位数字')
        return v

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('密码至少8位')
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class CompleteOnboardingResponse(BaseModel):
    """Response schema for completing onboarding"""
    message: str = Field(..., description="Success message")
    onboarding_completed: bool = Field(True, description="Onboarding completion status")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    error_code: str = Field(None, description="Machine-readable error code")
