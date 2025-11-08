"""Authentication middleware and dependencies."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.models import User
from app.utils.security import decode_access_token

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # If DEBUG mode, always return mock user
    if settings.DEBUG:
        from datetime import datetime
        from app.models import OnboardingStatus
        # Create a mock user object
        mock_user = User(
            id=user_id,
            name=payload.get("name", "Demo User"),
            email=payload.get("email", "demo@example.com"),
            hashed_password="",
            onboarding_status=OnboardingStatus.COMPLETE,
            preferences={},
        )
        # Add timestamps for compatibility
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        return mock_user
    
    # Production mode: query database
    # This will only run if DEBUG=False
    from app.models import get_db
    db_gen = get_db()
    db = next(db_gen)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload is None:
            return None
        
        user_id: Optional[int] = payload.get("user_id")
        if user_id is None:
            return None
        
        # If DEBUG mode, return mock user
        if settings.DEBUG:
            from datetime import datetime
            from app.models import OnboardingStatus
            mock_user = User(
                id=user_id,
                name=payload.get("name", "Demo User"),
                email=payload.get("email", "demo@example.com"),
                hashed_password="",
                onboarding_status=OnboardingStatus.COMPLETE,
                preferences={},
            )
            # Add timestamps for compatibility
            mock_user.created_at = datetime.utcnow()
            mock_user.updated_at = datetime.utcnow()
            return mock_user
        
        # Production mode: query database
        from app.models import get_db
        db_gen = get_db()
        db = next(db_gen)
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()
    except Exception:
        return None

