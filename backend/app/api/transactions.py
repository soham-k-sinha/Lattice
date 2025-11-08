"""Transactions API routes - Fetch and sync transaction data from Knot"""
from typing import Any, Optional, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.middleware.auth import get_current_user
from app.models import User
from app.integrations.knot import KnotClient, KnotAPIError

router = APIRouter()

# In-memory storage for transactions (use database in production)
# Structure: { user_id: { merchant_id: { "transactions": [...], "next_cursor": str, "limit": int, "synced_at": ts } } }
TRANSACTIONS_CACHE: dict[int, Dict[str, Dict[str, Any]]] = {}


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
                "merchant": None,
                "transactions": [],
            }
        
        logger.info(f"User {current_user.id} has {len(accounts)} linked accounts")
        
        # Determine merchant to sync
        selected_account = None
        if merchant_id:
            merchant_id_str = str(merchant_id)
            for acc in accounts:
                if str(acc.merchant_id) == merchant_id_str:
                    selected_account = acc
                    break
            if not selected_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Merchant {merchant_id} not linked for this user"
                )
        else:
            # Default to the first linked merchant
            selected_account = accounts[0]
            logger.info(
                "No merchant_id provided, defaulting to merchant %s (%s)",
                selected_account.merchant_id,
                selected_account.merchant_name,
            )
        
        merchant_id_str = str(selected_account.merchant_id)
        
        logger.info(
            f"Syncing transactions for user {current_user.id}, merchant {selected_account.merchant_id} ({selected_account.merchant_name})"
        )
        
        sync_response = await knot.sync_transactions(
            external_user_id=str(current_user.id),
            merchant_id=str(selected_account.merchant_id),
            cursor=cursor,
            limit=limit,
        )
        
        transactions_payload = []
        for txn in sync_response.transactions:
            txn_payload = txn.model_dump() if hasattr(txn, "model_dump") else dict(txn)
            # Ensure merchant metadata is populated
            txn_payload.setdefault("merchant_id", selected_account.merchant_id)
            txn_payload.setdefault("merchant_name", selected_account.merchant_name)
            transactions_payload.append(txn_payload)
        
        merchant_payload = sync_response.merchant or {
            "id": int(selected_account.merchant_id)
            if str(selected_account.merchant_id).isdigit()
            else selected_account.merchant_id,
            "name": selected_account.merchant_name,
        }
        
        logger.info(
            "✅ Synced %s transaction(s) for merchant %s",
            len(transactions_payload),
            merchant_payload.get("name"),
        )
        
        # Cache results
        user_cache = TRANSACTIONS_CACHE.setdefault(current_user.id, {})
        user_cache[merchant_id_str] = {
            "transactions": transactions_payload,
            "next_cursor": sync_response.next_cursor,
            "limit": sync_response.limit or limit,
            "synced_at": datetime.utcnow().isoformat(),
            "merchant": merchant_payload,
        }
        
        return {
            "success": True,
            "merchant": merchant_payload,
            "transactions": transactions_payload,
            "total_count": len(transactions_payload),
            "next_cursor": sync_response.next_cursor,
            "has_more": sync_response.has_more,
            "limit": sync_response.limit or limit,
            "cursor": sync_response.next_cursor,
            "synced_at": user_cache[merchant_id_str]["synced_at"],
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
    
    user_cache = TRANSACTIONS_CACHE.get(current_user.id, {})
    
    if merchant_id:
        merchant_id_str = str(merchant_id)
        merchant_cache = user_cache.get(merchant_id_str, {})
        transactions = merchant_cache.get("transactions", [])[:limit]
        return {
            "success": True,
            "transactions": transactions,
            "total_count": len(transactions),
            "merchant": merchant_cache.get("merchant"),
            "next_cursor": merchant_cache.get("next_cursor"),
            "limit": merchant_cache.get("limit"),
            "synced_at": merchant_cache.get("synced_at"),
            "cached": True,
            "message": "Use /transactions/sync to fetch fresh data from Knot" if not transactions else None,
        }
    
    # Aggregate all merchants
    aggregated_transactions = []
    for merchant_data in user_cache.values():
        aggregated_transactions.extend(merchant_data.get("transactions", []))
    
    aggregated_transactions = aggregated_transactions[:limit]
    
    return {
        "success": True,
        "transactions": aggregated_transactions,
        "total_count": len(aggregated_transactions),
        "cached": True,
        "message": "Use /transactions/sync?merchant_id=<id> to fetch fresh data for a specific merchant",
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

