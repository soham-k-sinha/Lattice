"""Helpers for loading stored transaction data for users."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger

TRANSACTIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "transactions"


def load_user_transactions(user_id: int) -> Dict[str, Any]:
    """Load all stored transaction payloads for the given user."""
    if not TRANSACTIONS_DIR.exists():
        logger.debug("Transactions directory %s does not exist", TRANSACTIONS_DIR)
        return {}

    user_prefix = f"user_{user_id}_merchant_"
    purchases: Dict[str, Any] = {}

    for file_path in TRANSACTIONS_DIR.glob(f"{user_prefix}*.json"):
        merchant_id = file_path.stem.split("_")[-1]
        try:
            with file_path.open("r", encoding="utf-8") as fh:
                purchases[merchant_id] = json.load(fh)
        except json.JSONDecodeError:
            logger.warning(
                "Skipping malformed transactions file for user %s: %s",
                user_id,
                file_path,
            )
        except Exception as exc:
            logger.error(
                "Unexpected error loading transactions file %s: %s",
                file_path,
                exc,
            )

    return purchases

