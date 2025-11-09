"""Utility helpers for managing debug-mode user storage."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.models import OnboardingStatus
from app.utils.security import get_password_hash, verify_password


STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "users_store.json"


def _ensure_store_path() -> None:
    """Make sure the data directory exists."""
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _default_users() -> Dict[str, Any]:
    """Return the default seeded users for the store."""
    now = datetime.utcnow().isoformat()
    return {
        "next_id": 4,
        "users": [
            {
                "id": 1,
                "name": "Alice Demo",
                "email": "alice@demo.com",
                "hashed_password": get_password_hash("password123"),
                "onboarding_status": OnboardingStatus.COMPLETE.value,
                "preferences": {"theme": "dark", "notifications": True},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 2,
                "name": "Bob Test",
                "email": "bob@test.com",
                "hashed_password": get_password_hash("password123"),
                "onboarding_status": OnboardingStatus.COMPLETE.value,
                "preferences": {"theme": "light", "notifications": False},
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 3,
                "name": "Demo User",
                "email": "demo@example.com",
                "hashed_password": get_password_hash("demo123"),
                "onboarding_status": OnboardingStatus.INCOMPLETE.value,
                "preferences": {},
                "created_at": now,
                "updated_at": now,
            },
        ],
    }


def _load_store() -> Dict[str, Any]:
    """Load the JSON store from disk, seeding defaults if missing."""
    _ensure_store_path()

    if not STORE_PATH.exists():
        data = _default_users()
        _write_store(data)
        return data

    try:
        with STORE_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError:
        # Corrupted store, recreate with defaults
        data = _default_users()
        _write_store(data)
        return data


def _write_store(data: Dict[str, Any]) -> None:
    """Persist store to disk."""
    _ensure_store_path()
    with STORE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=True, indent=2)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve a stored user by email."""
    store = _load_store()
    norm_email = _normalize_email(email)
    return next((u for u in store["users"] if _normalize_email(u["email"]) == norm_email), None)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a stored user by ID."""
    store = _load_store()
    return next((u for u in store["users"] if u["id"] == user_id), None)


def create_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create and persist a new user record."""
    store = _load_store()
    if get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    norm_email = _normalize_email(email)
    now = datetime.utcnow().isoformat()

    new_user = {
        "id": store["next_id"],
        "name": name,
        "email": norm_email,
        "hashed_password": get_password_hash(password),
        "onboarding_status": OnboardingStatus.INCOMPLETE.value,
        "preferences": {},
        "created_at": now,
        "updated_at": now,
    }

    store["users"].append(new_user)
    store["next_id"] += 1
    _write_store(store)
    return new_user


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify the provided credentials."""
    user = get_user_by_email(email)
    if user and verify_password(password, user["hashed_password"]):
        return user
    return None


def update_user(user_id: int, **updates: Any) -> Optional[Dict[str, Any]]:
    """Update a stored user and persist changes."""
    store = _load_store()
    for idx, user in enumerate(store["users"]):
        if user["id"] == user_id:
            user.update(updates)
            user["updated_at"] = datetime.utcnow().isoformat()
            store["users"][idx] = user
            _write_store(store)
            return user
    return None

