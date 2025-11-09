"""Authentication API routes."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    SessionResponse,
    Token,
    UserLogin,
    UserResponse,
    UserSignup,
)
from app.config.settings import settings
from app.middleware.auth import get_current_user, get_current_user_optional
from app.models import OnboardingStatus, User, get_db
from app.utils.security import create_access_token, get_password_hash, verify_password
from app.utils import user_store

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignup) -> Token:
    """Register a new user."""
    # DEBUG mode: Use local JSON store for persistence
    if settings.DEBUG:
        new_user = user_store.create_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
        )
        access_token = create_access_token(
            data={
                "user_id": new_user["id"],
                "email": new_user["email"],
                "name": new_user["name"],
                "onboarding_status": new_user["onboarding_status"],
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token)
    
    # Production mode: Use database
    from app.models import get_db
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            onboarding_status=OnboardingStatus.INCOMPLETE,
            preferences={},
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": new_user.id, "email": new_user.email, "name": new_user.name}
        )
        
        return Token(access_token=access_token)
    finally:
        db.close()


@router.post("/login", response_model=Token)
def login(user_data: UserLogin) -> Token:
    """Authenticate user and return access token."""
    # DEBUG mode: Use mock authentication
    if settings.DEBUG:
        stored_user = user_store.authenticate_user(
            email=user_data.email,
            password=user_data.password,
        )
        if stored_user:
            access_token = create_access_token(
                data={
                    "user_id": stored_user["id"],
                    "email": stored_user["email"],
                    "name": stored_user["name"],
                    "onboarding_status": stored_user["onboarding_status"],
                },
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            return Token(access_token=access_token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Production mode: Use database
    from app.models import get_db
    db_gen = get_db()
    db = next(db_gen)
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_data.email).first()
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email, "name": user.name},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        return Token(access_token=access_token)
    finally:
        db.close()


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    """Logout user (client should discard token)."""
    # In a stateless JWT setup, logout is handled client-side
    # For production, you might want to implement token blacklisting
    return {"message": "Successfully logged out"}


@router.get("/session", response_model=SessionResponse)
def get_session(current_user: User = Depends(get_current_user_optional)) -> SessionResponse:
    """Get current session information."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    user_response = UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        onboarding_status=current_user.onboarding_status.value,
        preferences=current_user.preferences,
        created_at=current_user.created_at if hasattr(current_user, 'created_at') else None,
    )
    
    return SessionResponse(user=user_response, authenticated=True)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        onboarding_status=current_user.onboarding_status.value,
        preferences=current_user.preferences,
        created_at=current_user.created_at if hasattr(current_user, 'created_at') else None,
    )

