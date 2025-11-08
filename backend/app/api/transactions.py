"""Transactions API routes - Fetch and sync transaction data from Knot"""
from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.middleware.auth import get_current_user
from app.models import User
from app.integrations.knot import KnotClient, KnotAPIError

router = APIRouter()

# In-memory storage for transactions (use database in production)
TRANSACTIONS_CACHE: dict[int, list[dict]] = {}


@router.get("/sync")
async def sync_transactions(
    merchant_id: Optional[str] = Query(None, description="Merchant ID (e.g., '36' for Ubereats)"),
    limit: int = Query(100, ge=1, le=500, description="Max transactions to fetch"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Sync transactions from Knot for the current user
    
    - If merchant_id is provided, sync only that merchant
    - If merchant_id is None, sync all linked merchants
    """
    
    knot = KnotClient()
    
    try:
        # First, get user's linked accounts
        logger.info(f"Fetching accounts for user {current_user.id}")
        accounts = await knot.get_accounts(str(current_user.id))
        
        if not accounts:
            return {
                "success": False,
                "message": "No linked accounts found. Please complete onboarding first.",
                "transactions": [],
                "accounts": [],
            }
        
        logger.info(f"User {current_user.id} has {len(accounts)} linked accounts")
        
        # If specific merchant requested, filter to that one
        if merchant_id:
            accounts = [acc for acc in accounts if str(acc.merchant_id) == str(merchant_id)]
            if not accounts:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Merchant {merchant_id} not linked for this user"
                )
        
        # Sync transactions for each account
        all_transactions = []
        sync_results = []
        
        for account in accounts:
            try:
                logger.info(f"Syncing transactions for merchant {account.merchant_id} ({account.merchant_name})")
                
                # Call Knot API to sync transactions
                sync_response = await knot.sync_transactions(
                    external_user_id=str(current_user.id),
                    merchant_id=str(account.merchant_id),
                    cursor=cursor,
                    limit=limit,
                )
                
                logger.info(f"✅ Synced {len(sync_response.transactions)} transactions from {account.merchant_name}")
                
                # Add merchant info to each transaction
                for txn in sync_response.transactions:
                    txn_data = txn.dict() if hasattr(txn, 'dict') else txn
                    txn_data["merchant_name"] = account.merchant_name
                    txn_data["merchant_id"] = account.merchant_id
                    all_transactions.append(txn_data)
                
                sync_results.append({
                    "merchant_id": account.merchant_id,
                    "merchant_name": account.merchant_name,
                    "count": len(sync_response.transactions),
                    "has_more": sync_response.has_more,
                    "next_cursor": sync_response.next_cursor,
                })
                
            except KnotAPIError as e:
                logger.error(f"Failed to sync {account.merchant_name}: {e}")
                sync_results.append({
                    "merchant_id": account.merchant_id,
                    "merchant_name": account.merchant_name,
                    "error": str(e),
                    "count": 0,
                })
        
        # Cache transactions in memory
        TRANSACTIONS_CACHE[current_user.id] = all_transactions
        
        logger.info(f"✅ Total synced: {len(all_transactions)} transactions")
        
        return {
            "success": True,
            "transactions": all_transactions,
            "total_count": len(all_transactions),
            "synced_merchants": sync_results,
            "accounts": [
                {
                    "id": acc.id,
                    "merchant_id": acc.merchant_id,
                    "merchant_name": acc.merchant_name,
                    "status": acc.status,
                }
                for acc in accounts
            ],
        }
        
    except KnotAPIError as e:
        logger.error(f"Knot API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Knot API Error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error syncing transactions: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        await knot.close()


@router.get("")
async def get_transactions(
    merchant_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get cached transactions for the current user
    
    Returns transactions from cache. Call /sync first to fetch fresh data.
    """
    
    user_transactions = TRANSACTIONS_CACHE.get(current_user.id, [])
    
    # Filter by merchant if requested
    if merchant_id:
        user_transactions = [
            txn for txn in user_transactions 
            if str(txn.get("merchant_id")) == str(merchant_id)
        ]
    
    # Apply limit
    user_transactions = user_transactions[:limit]
    
    return {
        "success": True,
        "transactions": user_transactions,
        "total_count": len(user_transactions),
        "cached": True,
        "message": "Use /transactions/sync to fetch fresh data from Knot" if not user_transactions else None,
    }


@router.get("/{transaction_id}")
async def get_transaction_details(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get detailed information for a specific transaction"""
    
    knot = KnotClient()
    
    try:
        logger.info(f"Fetching transaction {transaction_id}")
        transaction = await knot.get_transaction(transaction_id)
        
        return {
            "success": True,
            "transaction": transaction,
        }
        
    except KnotAPIError as e:
        logger.error(f"Knot API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if e.status_code == 404 else status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Transaction not found or API error: {e.message}"
        )
    finally:
        await knot.close()

