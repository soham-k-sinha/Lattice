"""Onboarding API routes - Knot integration"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from loguru import logger

from app.config.settings import settings
from app.integrations.knot import KnotClient, KnotAPIError
from app.middleware.auth import get_current_user
from app.models import User
from app.api.mock_data import MOCK_ACCOUNTS

router = APIRouter()


# In-memory storage for Knot accounts (no database needed)
KNOT_LINKED_ACCOUNTS = {}  # user_id -> list of accounts


# ==================== REQUEST/RESPONSE MODELS ====================

class OnboardingStartRequest(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    test_mode: Optional[bool] = False  # Use unique ID for testing to avoid Knot session conflicts


class OnboardingStartResponse(BaseModel):
    session_token: str
    session_id: str
    expires_at: str
    sandbox_mode: bool
    environment: str  # "development" or "production"


class OnboardingCompleteRequest(BaseModel):
    session_id: str


class OnboardingCompleteResponse(BaseModel):
    success: bool
    accounts_linked: int
    message: str


# ==================== ENDPOINTS ====================

@router.post("/start", response_model=OnboardingStartResponse)
async def start_onboarding(
    request: OnboardingStartRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Start Knot onboarding flow
    Returns a session_token to pass to Knot SDK
    """
    
    # Mock mode (feature flag off or no credentials)
    if not settings.FEATURE_KNOT:
        logger.info(f"Mock onboarding for user {current_user.id}")
        return OnboardingStartResponse(
            session_token="mock_token_" + str(current_user.id),
            session_id="mock_session_" + str(current_user.id),
            expires_at="2025-12-31T23:59:59Z",
            sandbox_mode=True,
            environment=settings.KNOT_ENVIRONMENT,
        )
    
    # Real Knot integration
    knot = KnotClient()
    try:
        contact = {"email": request.email}
        if request.phone:
            contact["phone"] = request.phone
        
        # Use unique ID for testing to avoid Knot session conflicts
        # Knot recommends using different external_user_id for consecutive tests
        if request.test_mode:
            from time import time
            external_user_id = f"test_{current_user.id}_{int(time())}"
            logger.info(f"Test mode: Using unique external_user_id: {external_user_id}")
        else:
            external_user_id = str(current_user.id)
        
        session = await knot.create_session(
            external_user_id=external_user_id,
            contact=contact,
            session_type="transaction_link",
        )
        
        logger.info(f"Knot session created for user {current_user.id}: {session.session_id}")
        
        # Knot API only returns 'session' field, use it for both session_id and session_token
        from datetime import datetime, timedelta
        expires_at = session.expires_at or (datetime.utcnow() + timedelta(minutes=30)).isoformat() + "Z"
        
        return OnboardingStartResponse(
            session_token=session.session_token or session.session_id,  # Use session_id if token not provided
            session_id=session.session_id,
            expires_at=expires_at,
            sandbox_mode=False,
            environment=settings.KNOT_ENVIRONMENT,
        )
        
    except KnotAPIError as e:
        logger.error(f"Knot API error: {e}")
        # Fallback to mock mode on error
        return OnboardingStartResponse(
            session_token="mock_token_" + str(current_user.id),
            session_id="mock_session_" + str(current_user.id),
            expires_at="2025-12-31T23:59:59Z",
            sandbox_mode=True,
            environment=settings.KNOT_ENVIRONMENT,
        )
    finally:
        await knot.close()


@router.post("/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Complete onboarding - fetch and store linked accounts
    Called after user finishes Knot SDK flow
    """
    
    # Mock mode
    if not settings.FEATURE_KNOT:
        logger.info(f"Mock onboarding complete for user {current_user.id}")
        # Store some mock accounts for this user
        KNOT_LINKED_ACCOUNTS[current_user.id] = [
            {
                "id": f"mock_account_{current_user.id}_1",
                "user_id": current_user.id,
                "institution": "Amazon",
                "account_name": "Amazon Account",
                "account_type": "transaction_link",
                "balance": 0.0,
                "currency": "USD",
                "permissions": {"transactions": True, "cards": True},
                "status": "active",
                "last_synced": datetime.utcnow().isoformat(),
                "knot_account_id": None,
                "knot_merchant_id": "amazon",
            }
        ]
        return OnboardingCompleteResponse(
            success=True,
            accounts_linked=1,
            message="Mock onboarding completed - 1 account linked",
        )
    
    # Real Knot integration
    knot = KnotClient()
    try:
        # Fetch accounts from Knot
        accounts = await knot.get_accounts(str(current_user.id))
        
        # Store in memory
        user_accounts = []
        for knot_account in accounts:
            account_data = {
                "id": knot_account.id,
                "user_id": current_user.id,
                "institution": knot_account.merchant_name,
                "account_name": f"{knot_account.merchant_name} Account",
                "account_type": "transaction_link",
                "balance": 0.0,  # Knot doesn't provide balance
                "currency": "USD",
                "permissions": knot_account.permissions,
                "status": knot_account.status,
                "last_synced": datetime.utcnow().isoformat(),
                "knot_account_id": knot_account.id,
                "knot_merchant_id": knot_account.merchant_id,
            }
            user_accounts.append(account_data)
        
        KNOT_LINKED_ACCOUNTS[current_user.id] = user_accounts
        
        logger.info(f"Onboarding complete for user {current_user.id}: {len(accounts)} accounts linked")
        
        return OnboardingCompleteResponse(
            success=True,
            accounts_linked=len(accounts),
            message=f"Successfully linked {len(accounts)} accounts",
        )
        
    except KnotAPIError as e:
        logger.error(f"Knot API error: {e}")
        # Fallback to mock
        KNOT_LINKED_ACCOUNTS[current_user.id] = []
        return OnboardingCompleteResponse(
            success=True,
            accounts_linked=0,
            message="Completed with fallback mode",
        )
    finally:
        await knot.close()

