"""Transactions API routes - Fetch and sync transaction data from Knot"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.middleware.auth import get_current_user
from app.models import User
from app.integrations.knot import KnotClient, KnotAPIError
from app.integrations.knot_types import KnotAccount
from app.api.onboarding import KNOT_EXTERNAL_IDS

router = APIRouter()

# In-memory storage for transactions (use database in production)
# Structure: { user_id: { merchant_id: { "transactions": [...], "next_cursor": str, "limit": int, "synced_at": ts } } }
TRANSACTIONS_CACHE: dict[int, Dict[str, Dict[str, Any]]] = {}

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "transactions"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_TRANSACTION_TEMPLATES: Dict[str, list[dict[str, Any]]] = {
    "ubereats": [
        {
            "days_ago": 2,
            "restaurant": "Green Bowl Salads",
            "items": [
                {"name": "Harvest Bowl", "quantity": 1, "price": 11.95},
                {"name": "Sparkling Water", "quantity": 1, "price": 2.25},
            ],
            "subtotal": 14.20,
            "tax": 1.11,
            "tip": 2.50,
            "delivery_fee": 1.49,
            "status": "DELIVERED",
        },
        {
            "days_ago": 7,
            "restaurant": "Sunrise Diner",
            "items": [
                {"name": "Breakfast Burrito", "quantity": 1, "price": 9.50},
                {"name": "Cold Brew", "quantity": 1, "price": 3.75},
            ],
            "subtotal": 13.25,
            "tax": 1.08,
            "tip": 2.00,
            "delivery_fee": 0.99,
            "status": "DELIVERED",
        },
        {
            "days_ago": 14,
            "restaurant": "Little Kyoto Sushi",
            "items": [
                {"name": "Salmon Roll", "quantity": 1, "price": 8.95},
                {"name": "California Roll", "quantity": 1, "price": 7.95},
                {"name": "Miso Soup", "quantity": 1, "price": 2.50},
            ],
            "subtotal": 19.40,
            "tax": 1.59,
            "tip": 3.00,
            "delivery_fee": 1.49,
            "status": "DELIVERED",
        },
    ],
}

SAMPLE_MERCHANT_ALIASES = {
    "36": "ubereats",
    "ubereats": "ubereats",
    "uber eats": "ubereats",
}


def _dump_transactions_to_file(user_id: int, merchant_id: str, payload: Dict[str, Any]) -> Path:
    """Persist the latest transaction payload to disk for debugging/analysis."""
    file_path = DATA_DIR / f"user_{user_id}_merchant_{merchant_id}.json"
    try:
        with file_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        logger.info("🗂️ Saved transactions to %s", file_path)
    except Exception as dump_err:
        logger.error("Failed to write transactions file %s: %s", file_path, dump_err)
    return file_path


def _normalize_transaction(
    raw_txn: Any,
    merchant_id: str,
    merchant_name: str,
) -> Dict[str, Any]:
    txn_payload = raw_txn.model_dump() if hasattr(raw_txn, "model_dump") else dict(raw_txn)
    txn_payload.setdefault("merchant_id", merchant_id)
    txn_payload.setdefault("merchant_name", merchant_name)

    price = txn_payload.get("price") or {}
    if not isinstance(price, dict):
        price = {}
    txn_payload["price"] = price

    amount_candidate = (
        price.get("amount")
        or price.get("total")
        or price.get("final_total")
        or price.get("sub_total")
        or txn_payload.get("amount")
    )
    if amount_candidate is not None:
        try:
            txn_payload["price_amount"] = float(amount_candidate)
        except (TypeError, ValueError):
            pass

    txn_payload["price_currency"] = price.get("currency", "USD")

    metadata = txn_payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    txn_payload["metadata"] = metadata

    txn_payload["order_id"] = (
        metadata.get("order_id")
        or metadata.get("external_id")
        or txn_payload.get("external_id")
        or txn_payload.get("id")
    )
    txn_payload["transaction_status"] = (
        txn_payload.get("order_status")
        or metadata.get("status")
        or metadata.get("order_status")
    )

    return txn_payload


def _build_sample_transactions(merchant_id: str, merchant_name: str) -> list[dict[str, Any]]:
    candidates = [
        merchant_id.lower(),
        (merchant_name or "").lower(),
        (merchant_name or "").lower().replace(" ", ""),
    ]
    template_key = None
    for candidate in candidates:
        alias = SAMPLE_MERCHANT_ALIASES.get(candidate, candidate)
        if alias in SAMPLE_TRANSACTION_TEMPLATES:
            template_key = alias
            break

    if not template_key:
        return []

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    samples: list[dict[str, Any]] = []

    for idx, template in enumerate(SAMPLE_TRANSACTION_TEMPLATES[template_key], start=1):
        total = (
            template["subtotal"]
            + template.get("tax", 0.0)
            + template.get("tip", 0.0)
            + template.get("delivery_fee", 0.0)
        )
        order_dt = now - timedelta(days=template["days_ago"])
        order_id = template.get("order_id") or f"{merchant_name[:2].upper()}-{order_dt.strftime('%Y%m%d')}-{idx:03d}"

        sample_tx = {
            "id": f"sample-{template_key}-{idx}",
            "merchant_id": merchant_id,
            "merchant_name": merchant_name,
            "external_id": order_id,
            "datetime": order_dt.isoformat(),
            "url": template.get("url"),
            "order_status": template.get("status", "DELIVERED"),
            "payment_methods": [
                {
                    "type": "CARD",
                    "brand": template.get("card_brand", "VISA"),
                    "transaction_amount": f"{total:.2f}",
                    "last_four": template.get("last_four", "4242"),
                }
            ],
            "price": {
                "amount": f"{total:.2f}",
                "currency": "USD",
                "sub_total": f"{template['subtotal']:.2f}",
                "tax": f"{template.get('tax', 0.0):.2f}",
                "tip": f"{template.get('tip', 0.0):.2f}",
                "adjustments": [],
            },
            "products": [
                {
                    "name": item["name"],
                    "quantity": item.get("quantity", 1),
                    "price": f"{item.get('price', 0.0):.2f}",
                }
                for item in template.get("items", [])
            ],
            "metadata": {
                "order_id": order_id,
                "status": template.get("status", "DELIVERED"),
                "restaurant": template.get("restaurant"),
                "source": "sample",
            },
        }

        delivery_fee = template.get("delivery_fee")
        if delivery_fee:
            sample_tx["price"]["adjustments"].append(
                {"type": "FEE", "label": "Delivery Fee", "amount": f"{delivery_fee:.2f}"}
            )

        samples.append(sample_tx)

    return samples


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
        external_user_id = KNOT_EXTERNAL_IDS.get(current_user.id, str(current_user.id))
        try:
            accounts = await knot.get_accounts(external_user_id)
        except KnotAPIError as account_err:
            logger.warning(
                "Failed to fetch accounts for user %s (external_user_id=%s): %s",
                current_user.id,
                external_user_id,
                account_err,
            )
            # Fallback to stored in-memory onboarding accounts if available
            from app.api.onboarding import KNOT_LINKED_ACCOUNTS

            stored_accounts = KNOT_LINKED_ACCOUNTS.get(current_user.id)
            if stored_accounts:
                accounts = [
                    KnotAccount(
                        id=str(acc["knot_account_id"] or acc["id"]),
                        merchant_id=str(acc["knot_merchant_id"]),
                        merchant_name=str(acc["institution"]),
                        status=str(acc.get("status", "active")),
                        permissions=acc.get("permissions") or {},
                        linked_at=acc.get("last_synced"),
                    )
                    for acc in stored_accounts
                    if acc.get("knot_merchant_id")
                ]
            else:
                raise
        
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
            merchant_id_str = str(merchant_id).lower()
            for acc in accounts:
                acc_id = str(acc.id).lower()
                acc_merchant_id = str(acc.merchant_id).lower()
                acc_name = acc.merchant_name.lower()
                if (
                    merchant_id_str in {acc_id, acc_merchant_id, acc_name}
                    or merchant_id_str == acc_name.replace(" ", "")
                ):
                    selected_account = acc
                    break
            if not selected_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Merchant {merchant_id} not linked for this user",
                )
        else:
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
            external_user_id=external_user_id,
            merchant_id=str(selected_account.merchant_id),
            account_id=str(selected_account.id),
            cursor=cursor,
            limit=limit,
        )
        
        transactions_payload = [
            _normalize_transaction(
                txn,
                str(selected_account.merchant_id),
                selected_account.merchant_name,
            )
            for txn in sync_response.transactions
        ]
        
        merchant_payload = sync_response.merchant or {
            "id": int(selected_account.merchant_id)
            if str(selected_account.merchant_id).isdigit()
            else selected_account.merchant_id,
            "name": selected_account.merchant_name,
        }

        fallback_used = False

        if not transactions_payload:
            logger.warning(
                "Knot returned 0 transactions for user %s merchant %s; attempting sample fallback.",
                current_user.id,
                merchant_payload.get("name"),
            )
            sample_transactions = _build_sample_transactions(
                str(selected_account.merchant_id),
                selected_account.merchant_name,
            )
            if sample_transactions:
                fallback_used = True
                transactions_payload = [
                    _normalize_transaction(
                        txn,
                        str(selected_account.merchant_id),
                        selected_account.merchant_name,
                    )
                    for txn in sample_transactions
                ]
                logger.info(
                    "Loaded %s sample transaction(s) for merchant %s",
                    len(transactions_payload),
                    merchant_payload.get("name"),
                )
        
        logger.info(
            "✅ Synced %s transaction(s) for merchant %s",
            len(transactions_payload),
            merchant_payload.get("name"),
        )
        
        # Cache results
        user_cache = TRANSACTIONS_CACHE.setdefault(current_user.id, {})
        user_cache_entry = {
            "transactions": transactions_payload,
            "next_cursor": sync_response.next_cursor,
            "limit": sync_response.limit or limit,
            "synced_at": datetime.utcnow().isoformat(),
            "merchant": merchant_payload,
        }
        user_cache[merchant_id_str] = user_cache_entry
        raw_response = sync_response.model_dump()
        if fallback_used:
            raw_response = {
                **raw_response,
                "fallback": "sample_transactions",
                "transactions": transactions_payload,
            }
        user_cache_entry["raw_response"] = raw_response

        file_path = _dump_transactions_to_file(
            current_user.id,
            merchant_id_str,
            {
                "synced_at": user_cache[merchant_id_str]["synced_at"],
                "merchant": merchant_payload,
                "transactions": transactions_payload,
                "next_cursor": sync_response.next_cursor,
                "has_more": sync_response.has_more,
                "limit": sync_response.limit or limit,
                "raw_response": raw_response,
            },
        )
        
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
            "file_path": str(file_path),
            "raw_response": raw_response,
            "fallback_used": fallback_used,
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
            "file_path": str(DATA_DIR / f"user_{current_user.id}_merchant_{merchant_id_str}.json")
            if merchant_cache
            else None,
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

