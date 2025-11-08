"""Pydantic models for Knot API responses"""
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, List, Dict, Any


class KnotSession(BaseModel):
    """Response from POST /session/create"""
    model_config = ConfigDict(populate_by_name=True)
    
    session: str  # Knot returns "session" not "session_id"
    session_token: Optional[str] = None
    expires_at: Optional[str] = None
    
    # Computed property for backward compatibility
    @computed_field
    @property
    def session_id(self) -> str:
        """Return session as session_id for backward compatibility"""
        return self.session


class KnotMerchant(BaseModel):
    """Merchant from POST /merchant/list"""
    id: str
    name: str
    logo_url: Optional[str] = None
    supported_features: List[str] = []


class KnotAccount(BaseModel):
    """Account from GET /accounts/get"""
    id: str
    merchant_id: str
    merchant_name: str
    status: str
    permissions: Dict[str, Any] = Field(default_factory=dict)
    linked_at: str


class KnotTransaction(BaseModel):
    """Transaction from POST /transactions/sync"""
    model_config = ConfigDict(extra="allow")

    id: str
    merchant_id: Optional[str] = None
    external_id: Optional[str] = None
    datetime: Optional[str] = None
    url: Optional[str] = None
    order_status: Optional[str] = None
    payment_methods: Optional[List[Dict[str, Any]]] = None
    price: Optional[Dict[str, Any]] = None
    products: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnotTransactionSyncResponse(BaseModel):
    """Response from POST /transactions/sync"""
    merchant: Optional[Dict[str, Any]] = None
    transactions: List[KnotTransaction]
    next_cursor: Optional[str] = None
    has_more: Optional[bool] = None
    limit: Optional[int] = None

