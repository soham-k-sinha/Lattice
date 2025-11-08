"""Accounts API routes."""
from typing import Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.mock_data import MOCK_ACCOUNTS
from app.middleware.auth import get_current_user
from app.models import User
from app.config.settings import settings
from app.integrations.knot import KnotClient, KnotAPIError

router = APIRouter()

# Import in-memory storage from onboarding
from app.api.onboarding import KNOT_LINKED_ACCOUNTS


@router.get("")
async def get_accounts(
    current_user: User = Depends(get_current_user),
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Get all linked accounts for the current user."""
    
    # Check if user has Knot accounts (from onboarding)
    if current_user.id in KNOT_LINKED_ACCOUNTS:
        user_accounts = KNOT_LINKED_ACCOUNTS[current_user.id]
        
        # Optionally refresh from Knot if requested
        if force_refresh and settings.FEATURE_KNOT:
            knot = KnotClient()
            try:
                knot_accounts = await knot.get_accounts(str(current_user.id))
                
                # Update in-memory storage
                updated_accounts = []
                for knot_acc in knot_accounts:
                    account_data = {
                        "id": knot_acc.id,
                        "user_id": current_user.id,
                        "institution": knot_acc.merchant_name,
                        "account_name": f"{knot_acc.merchant_name} Account",
                        "account_type": "transaction_link",
                        "balance": 0.0,
                        "currency": "USD",
                        "permissions": knot_acc.permissions,
                        "status": knot_acc.status,
                        "last_synced": datetime.utcnow().isoformat(),
                        "knot_account_id": knot_acc.id,
                        "knot_merchant_id": knot_acc.merchant_id,
                    }
                    updated_accounts.append(account_data)
                
                KNOT_LINKED_ACCOUNTS[current_user.id] = updated_accounts
                user_accounts = updated_accounts
                logger.info(f"Refreshed {len(updated_accounts)} accounts from Knot")
                
            except KnotAPIError as e:
                logger.error(f"Failed to refresh from Knot: {e}")
                # Use cached data
            finally:
                await knot.close()
        
        return {
            "accounts": user_accounts,
            "total": len(user_accounts),
            "sandbox_mode": not settings.FEATURE_KNOT,
        }
    
    # Fallback to mock accounts
    user_accounts = [
        acc for acc in MOCK_ACCOUNTS 
        if acc["user_id"] == current_user.id
    ]
    
    return {
        "accounts": user_accounts,
        "total": len(user_accounts),
        "sandbox_mode": True,
    }


@router.get("/status")
def get_accounts_status(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Get account connection status."""
    return {
        "connected": len(MOCK_ACCOUNTS) > 0,
        "total_accounts": len(MOCK_ACCOUNTS),
        "sandbox_mode": True,
        "last_sync": "2025-01-01T00:00:00Z",
    }


@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Delete/unlink a connected account."""
    # Find account
    account_index = None
    for i, acc in enumerate(MOCK_ACCOUNTS):
        if acc["id"] == account_id and acc["user_id"] == current_user.id:
            account_index = i
            break
    
    if account_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or not owned by user",
        )
    
    # Remove account
    deleted_account = MOCK_ACCOUNTS.pop(account_index)
    
    return {
        "message": f"Account {deleted_account['institution']} successfully unlinked",
        "account_id": str(account_id),
    }

