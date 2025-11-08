"""Knot API Integration Client"""
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from typing import Optional, List, Dict, Any
import base64
from loguru import logger

from app.config.settings import settings
from app.integrations.knot_types import (
    KnotSession,
    KnotMerchant,
    KnotAccount,
    KnotTransactionSyncResponse,
)


class KnotAPIError(Exception):
    """Custom exception for Knot API errors"""
    def __init__(self, status_code: int, message: str, response: Dict[str, Any]):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"Knot API Error {status_code}: {message}")


class KnotClient:
    """Client for Knot API - Commerce account linking and transactions"""
    
    def __init__(self):
        # Use the base URL from settings
        self.base_url = settings.KNOT_API_URL
        self.client_id = settings.KNOT_CLIENT_ID
        self.client_secret = settings.KNOT_CLIENT_SECRET
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("KNOT_CLIENT_ID and KNOT_CLIENT_SECRET not set - using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        if not self.mock_mode:
            # Create Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            self.headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            
            # HTTP client
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True,
            )
            
            logger.info(f"KnotClient initialized with base URL: {self.base_url}")
        else:
            self.client = None
            logger.info("KnotClient initialized in mock mode")
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
    
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        if self.mock_mode or not self.client:
            raise KnotAPIError(
                status_code=500,
                message="Knot client not configured - set KNOT_CLIENT_ID and KNOT_CLIENT_SECRET",
                response={},
            )
        
        try:
            logger.debug(f"Knot API {method} {endpoint}")
            response = await self.client.request(method, endpoint, **kwargs)
            
            # Log response for debugging
            logger.debug(f"Knot API response: {response.status_code}")
            
            # Handle error responses
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise KnotAPIError(
                    status_code=response.status_code,
                    message=error_data.get("message", "Unknown error"),
                    response=error_data,
                )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Knot API HTTP error: {e}")
            raise KnotAPIError(
                status_code=e.response.status_code,
                message=str(e),
                response=e.response.json() if e.response.content else {},
            )
        except httpx.HTTPError as e:
            logger.error(f"Knot API error: {e}")
            raise
    
    # ==================== SESSION MANAGEMENT ====================
    
    async def create_session(
        self,
        external_user_id: str,
        contact: Dict[str, str],
        session_type: str = "transaction_link",
    ) -> KnotSession:
        """
        Create Knot Link session for onboarding
        
        Args:
            external_user_id: Your internal user ID (string)
            contact: {"email": "user@example.com", "phone": "+1234567890"} (phone optional)
            session_type: "transaction_link" or "link"
        
        Returns:
            KnotSession with session_id, session_token, expires_at
        """
        payload = {
            "type": session_type,
            "external_user_id": external_user_id,
            "contact": contact,
        }
        
        logger.info(f"Creating Knot session for user {external_user_id}")
        result = await self._request("POST", "/session/create", json=payload)
        return KnotSession(**result)
    
    async def extend_session(self, session_id: str) -> KnotSession:
        """Extend an existing session"""
        payload = {"session_id": session_id}
        result = await self._request("POST", "/session/extend", json=payload)
        return KnotSession(**result)
    
    # ==================== MERCHANTS ====================
    
    async def list_merchants(
        self,
        merchant_type: str = "transaction_link",
    ) -> List[KnotMerchant]:
        """
        Get list of supported merchants
        
        Args:
            merchant_type: "transaction_link" or "card_switcher"
        
        Returns:
            List of KnotMerchant objects
        """
        payload = {"type": merchant_type}
        result = await self._request("POST", "/merchant/list", json=payload)
        merchants_data = result.get("merchants", [])
        return [KnotMerchant(**m) for m in merchants_data]
    
    # ==================== ACCOUNTS ====================
    
    async def get_accounts(
        self,
        external_user_id: str,
        merchant_id: Optional[str] = None,
    ) -> List[KnotAccount]:
        """
        Get all linked accounts for a user
        
        Args:
            external_user_id: Your internal user ID
            merchant_id: Optional filter by specific merchant
        
        Returns:
            List of KnotAccount objects
        """
        params = {"external_user_id": external_user_id}
        if merchant_id:
            params["merchant_id"] = merchant_id
        
        logger.info(f"Fetching accounts for user {external_user_id}")
        result = await self._request("GET", "/accounts/get", params=params)
        accounts_data = result.get("accounts", [])
        return [KnotAccount(**a) for a in accounts_data]
    
    # ==================== TRANSACTIONS ====================
    
    async def sync_transactions(
        self,
        external_user_id: str,
        merchant_id: str,
        cursor: Optional[str] = None,
        limit: int = 100,
    ) -> KnotTransactionSyncResponse:
        """
        Sync transactions for a specific merchant
        
        Args:
            external_user_id: Your internal user ID
            merchant_id: Merchant to sync (e.g., "amazon", "doordash")
            cursor: Pagination cursor from previous response
            limit: Max transactions per request
        
        Returns:
            KnotTransactionSyncResponse with transactions, next_cursor, has_more
        """
        payload = {
            "external_user_id": external_user_id,
            "merchant_id": merchant_id,
            "limit": limit,
        }
        
        if cursor:
            payload["cursor"] = cursor
        
        logger.info(f"Syncing transactions for {merchant_id}, user {external_user_id}")
        result = await self._request("POST", "/transactions/sync", json=payload)
        return KnotTransactionSyncResponse(**result)
    
    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get details for a specific transaction"""
        return await self._request("GET", f"/transactions/{transaction_id}")
    
    # ==================== USER MANAGEMENT ====================
    
    async def delete_user(self, external_user_id: str) -> Dict[str, Any]:
        """Delete all Knot data for a user"""
        payload = {"external_user_id": external_user_id}
        return await self._request("POST", "/user/delete", json=payload)


# Singleton instance (optional, for dependency injection)
_knot_client: Optional[KnotClient] = None


async def get_knot_client() -> KnotClient:
    """FastAPI dependency for KnotClient"""
    global _knot_client
    if _knot_client is None:
        _knot_client = KnotClient()
    return _knot_client

