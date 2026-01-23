"""
FastAPI Dependencies for Authentication
JWT token verification and user context injection
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Validates JWT token and retrieves user from database.
    Injects user object into request context.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authentication successful

    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode and validate JWT token
        payload = decode_access_token(token)

        # Extract user ID from token payload
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency

    Returns User if valid token provided, None otherwise.
    Useful for endpoints that have different behavior for authenticated/unauthenticated users.

    Args:
        credentials: Optional HTTP Bearer token
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: int = payload.get("user_id")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        return user

    except JWTError:
        return None


# Example usage in protected endpoints:
# @router.get("/protected")
# async def protected_route(current_user: User = Depends(get_current_user)):
#     return {"user_id": current_user.id, "phone": current_user.phone}
