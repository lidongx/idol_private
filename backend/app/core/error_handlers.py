"""
Global exception handlers for FastAPI application
"""
import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from asyncio import TimeoutError

from app.core.exceptions import IdolPrivateException, ErrorCodes

# Configure logger
logger = logging.getLogger(__name__)


async def idol_private_exception_handler(
    request: Request,
    exc: IdolPrivateException
) -> JSONResponse:
    """
    Handle custom IdolPrivateException errors

    Returns standardized error response with error_code and message
    """
    # Log the error
    logger.error(
        f"IdolPrivateException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors

    Returns user-friendly validation error messages
    """
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    error_message = "; ".join(errors)

    # Log validation error
    logger.warning(
        f"Validation error: {error_message}",
        extra={
            "error_code": ErrorCodes.VALIDATION_ERROR,
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": ErrorCodes.VALIDATION_ERROR,
            "message": "请求参数有误",
            "detail": error_message,
            "errors": exc.errors(),
        }
    )


async def timeout_exception_handler(
    request: Request,
    exc: TimeoutError
) -> JSONResponse:
    """
    Handle asyncio TimeoutError (AI generation timeout)

    Returns AI timeout error response
    """
    # Log timeout
    logger.error(
        "AI generation timeout",
        extra={
            "error_code": ErrorCodes.AI_TIMEOUT,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error_code": ErrorCodes.AI_TIMEOUT,
            "message": "AI响应超时，请稍后重试~",
            "detail": "AI生成时间超过30秒",
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle all other unhandled exceptions

    Returns generic service error response and logs full traceback
    """
    # Log full exception with traceback
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "error_code": ErrorCodes.SERVICE_ERROR,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )

    # Don't expose internal error details to users
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": ErrorCodes.SERVICE_ERROR,
            "message": "服务暂时有点忙，请稍后再试",
            "detail": "内部服务错误",
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app

    Usage:
        from app.core.error_handlers import register_exception_handlers
        register_exception_handlers(app)
    """
    # Custom exceptions
    app.add_exception_handler(IdolPrivateException, idol_private_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Timeout errors
    app.add_exception_handler(TimeoutError, timeout_exception_handler)

    # General exceptions (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered successfully")
