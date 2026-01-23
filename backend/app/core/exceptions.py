"""
Custom exceptions and error handling for idol_private API
"""
from fastapi import HTTPException, status


class IdolPrivateException(HTTPException):
    """Base exception for idol_private application"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: str = None
    ):
        self.error_code = error_code
        self.message = message
        super().__init__(
            status_code=status_code,
            detail=detail or message
        )


class NetworkException(IdolPrivateException):
    """Network-related errors"""

    def __init__(self, message: str = "网络连接失败"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="NETWORK_ERROR",
            message=message
        )


class AITimeoutException(IdolPrivateException):
    """AI generation timeout errors"""

    def __init__(self, message: str = "AI响应超时，请稍后重试"):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code="AI_TIMEOUT",
            message=message
        )


class QuotaExceededException(IdolPrivateException):
    """Message quota exceeded errors"""

    def __init__(self, message: str = "今天的免费额度用完啦"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="QUOTA_EXCEEDED",
            message=message
        )


class ServiceException(IdolPrivateException):
    """Internal service errors"""

    def __init__(self, message: str = "服务暂时有点忙，请稍后再试"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SERVICE_ERROR",
            message=message
        )


class ValidationException(IdolPrivateException):
    """Validation errors"""

    def __init__(self, message: str = "请求参数有误"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message
        )


class AuthenticationException(IdolPrivateException):
    """Authentication errors"""

    def __init__(self, message: str = "认证失败，请重新登录"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            message=message
        )


class ResourceNotFoundException(IdolPrivateException):
    """Resource not found errors"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message
        )


# Error code constants
class ErrorCodes:
    """Standardized error codes"""

    NETWORK_ERROR = "NETWORK_ERROR"
    AI_TIMEOUT = "AI_TIMEOUT"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    SERVICE_ERROR = "SERVICE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
