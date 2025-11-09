"""Authentication middleware and dependencies."""
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.models import User
from app.utils.security import decode_access_token
from app.utils import user_store

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
        from app.models import OnboardingStatus

        stored_user = user_store.get_user_by_id(user_id)
        if stored_user is not None:
            onboarding_status = stored_user.get("onboarding_status", OnboardingStatus.COMPLETE.value)
            preferences = stored_user.get("preferences") or {}
            created_at_raw = stored_user.get("created_at")
            updated_at_raw = stored_user.get("updated_at")

            debug_user = User(
                id=stored_user["id"],
                name=stored_user.get("name") or payload.get("name", "Demo User"),
                email=stored_user.get("email") or payload.get("email", "demo@example.com"),
                hashed_password=stored_user.get("hashed_password", ""),
                onboarding_status=OnboardingStatus(onboarding_status),
                preferences=preferences,
            )

            if created_at_raw:
                try:
                    debug_user.created_at = datetime.fromisoformat(created_at_raw)
                except ValueError:
                    debug_user.created_at = datetime.utcnow()
            else:
                debug_user.created_at = datetime.utcnow()

            if updated_at_raw:
                try:
                    debug_user.updated_at = datetime.fromisoformat(updated_at_raw)
                except ValueError:
                    debug_user.updated_at = datetime.utcnow()
            else:
                debug_user.updated_at = datetime.utcnow()

            return debug_user

        # Fallback to payload-only user
        mock_user = User(
            id=user_id,
            name=payload.get("name", "Demo User"),
            email=payload.get("email", "demo@example.com"),
            hashed_password="",
            onboarding_status=OnboardingStatus.COMPLETE,
            preferences={},
        )
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
            from app.models import OnboardingStatus
            stored_user = user_store.get_user_by_id(user_id)
            if stored_user is not None:
                onboarding_status = stored_user.get("onboarding_status", OnboardingStatus.COMPLETE.value)
                preferences = stored_user.get("preferences") or {}
                created_at_raw = stored_user.get("created_at")
                updated_at_raw = stored_user.get("updated_at")

                debug_user = User(
                    id=stored_user["id"],
                    name=stored_user.get("name") or payload.get("name", "Demo User"),
                    email=stored_user.get("email") or payload.get("email", "demo@example.com"),
                    hashed_password=stored_user.get("hashed_password", ""),
                    onboarding_status=OnboardingStatus(onboarding_status),
                    preferences=preferences,
                )

                if created_at_raw:
                    try:
                        debug_user.created_at = datetime.fromisoformat(created_at_raw)
                    except ValueError:
                        debug_user.created_at = datetime.utcnow()
                else:
                    debug_user.created_at = datetime.utcnow()

                if updated_at_raw:
                    try:
                        debug_user.updated_at = datetime.fromisoformat(updated_at_raw)
                    except ValueError:
                        debug_user.updated_at = datetime.utcnow()
                else:
                    debug_user.updated_at = datetime.utcnow()

                return debug_user

            mock_user = User(
                id=user_id,
                name=payload.get("name", "Demo User"),
                email=payload.get("email", "demo@example.com"),
                hashed_password="",
                onboarding_status=OnboardingStatus.COMPLETE,
                preferences={},
            )
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

