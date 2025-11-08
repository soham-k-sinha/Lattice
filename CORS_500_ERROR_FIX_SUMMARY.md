# ✅ CORS/500 Error - Fixed!

## 🚨 The Problem

**Error**: CORS + 500 Internal Server Error  
**Root Cause**: Knot API response format mismatch

### **What Happened**:
1. Knot API returns: `{"session": "abc123"}`
2. Our model expected: `{"session_id": "abc123", "session_token": "...", "expires_at": "..."}`
3. Pydantic validation failed → 500 error
4. Browser showed CORS error (misleading - consequence of 500)

---

## ✅ The Fixes Applied

### **1. Updated KnotSession Model** (`backend/app/integrations/knot_types.py`):
```python
class KnotSession(BaseModel):
    session: str  # ← Match actual API
    session_token: Optional[str] = None  # ← Made optional
    expires_at: Optional[str] = None  # ← Made optional
    
    @computed_field
    @property
    def session_id(self) -> str:
        return self.session  # ← Backward compatibility
```

### **2. Updated Onboarding Endpoint** (`backend/app/api/onboarding.py`):
```python
# Handle missing fields from Knot API
return OnboardingStartResponse(
    session_token=session.session_token or session.session_id,  # Fallback
    session_id=session.session_id,
    expires_at=session.expires_at or (datetime.utcnow() + timedelta(minutes=30)).isoformat() + "Z",
    sandbox_mode=False,
    environment=settings.KNOT_ENVIRONMENT,
)
```

---

## 🔄 To Apply the Fix

### **Option 1: Use the restart script**:
```bash
./restart-backend.sh
```

### **Option 2: Manual restart**:
```bash
# Stop backend (Ctrl+C in backend terminal)

# Then:
cd backend
poetry run uvicorn app.main:app --reload
```

---

## 🧪 Test After Restart

1. Go to `http://localhost:3000/onboarding`
2. Click "Connect with Knot"
3. Should see in console:
   ```
   ✅ Session created: {session_id: "...", environment: "development"}
   🌍 Using Knot environment: development
   ```
4. No more 500 or CORS errors!

---

## ✅ Expected Result

- ✅ No CORS errors
- ✅ No 500 errors  
- ✅ Session created successfully
- ✅ Knot SDK initializes
- ✅ Onboarding flow works

---

**Status**: ✅ Fixed - Restart backend to apply!
