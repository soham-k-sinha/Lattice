# 🎯 Knot Frontend Integration Plan

## 📊 Current State Analysis

### ✅ What Exists
- **Onboarding Page**: Beautiful 3-step UI with animations
- **API Client**: Well-structured with consistent patterns
- **Auth Flow**: Working JWT authentication
- **Error Handling**: Proper 401/403 handling with redirects

### 🎨 Design Principles
1. **Preserve existing UI/UX** - Keep the beautiful animations
2. **Follow existing patterns** - Match current API client style
3. **Add, don't replace** - Enhance, don't break
4. **Graceful degradation** - Handle errors elegantly

---

## 📋 Detailed Integration Plan

### **Phase 1: API Client Enhancement** (5 mins)

**File**: `frontend/lib/api.ts`

**Location**: After `logout()` method (line ~102), before `// ============= Chats =============`

**What to add**:
```typescript
// ============= Onboarding (Knot Integration) =============

async startOnboarding(email: string, phone?: string) {
  // Implementation matches existing patterns
},

async completeOnboarding(sessionId: string) {
  // Implementation matches existing patterns
},
```

**Why here?**
- Logical placement after authentication methods
- Before feature-specific sections (Chats, Groups, etc.)
- Maintains alphabetical-ish ordering

**Risks**: ⚠️ None - Adding new methods, not modifying existing

---

### **Phase 2: Onboarding Page Enhancement** (15 mins)

**File**: `frontend/app/onboarding/page.tsx`

**Current Behavior**:
```typescript
handleConnect() {
  setCurrentStep(1)
  setTimeout(() => setCurrentStep(2), 1500)
  setTimeout(() => setCurrentStep(3), 3000)
  setTimeout(() => router.push("/chat/main"), 4000)
}
```

**New Behavior**:
```typescript
handleConnect() {
  // Step 1: Start onboarding API call
  setCurrentStep(1)
  const result = await api.startOnboarding(...)
  
  // Step 2: Simulate processing (keep animation timing)
  setCurrentStep(2)
  await delay(1500)
  
  // Step 3: Complete onboarding API call
  const complete = await api.completeOnboarding(...)
  setCurrentStep(3)
  
  // Step 4: Redirect to accounts (not chat/main)
  setTimeout(() => router.push("/accounts"), 1000)
}
```

**Key Preservations**:
- ✅ Keep all 3 steps and animations
- ✅ Keep timing feel (users expect ~4 seconds)
- ✅ Keep existing UI components
- ✅ Keep motion animations

**Key Changes**:
- 🔄 Add real API calls during step transitions
- 🔄 Add error state and display
- 🔄 Add loading state management
- 🔄 Change redirect from `/chat/main` → `/accounts`
- 🔄 Get user email from somewhere (session or prop)

**Risks**: ⚠️ Low
- Existing structure is preserved
- Only enhancing the `handleConnect` function
- UI/animations stay the same

---

## 🔍 Implementation Details

### API Methods Specification

```typescript
interface OnboardingStartRequest {
  email: string
  phone?: string
}

interface OnboardingStartResponse {
  session_token: string
  session_id: string
  expires_at: string
  sandbox_mode: boolean
}

interface OnboardingCompleteResponse {
  success: boolean
  accounts_linked: number
  message: string
}
```

### Error Handling Strategy

1. **Network Errors**: Show user-friendly message, allow retry
2. **Auth Errors (401/403)**: Already handled by `fetchWithAuth`
3. **API Errors (500)**: Show error, offer to skip or retry
4. **Timeout**: Show error after 30s

### State Management

```typescript
// Existing
const [currentStep, setCurrentStep] = useState(0)

// New additions
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const [canRetry, setCanRetry] = useState(false)
```

---

## 🎨 UI Enhancements

### Error Display (new component)

Add after the steps, before the button:

```typescript
{error && (
  <motion.div
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: 1, y: 0 }}
    className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive/20"
  >
    <p className="text-sm text-destructive">{error}</p>
    {canRetry && (
      <Button 
        variant="outline" 
        size="sm" 
        onClick={handleRetry}
        className="mt-2"
      >
        Try Again
      </Button>
    )}
  </motion.div>
)}
```

### Button State Updates

```typescript
{currentStep === 0 && (
  <Button 
    onClick={handleConnect} 
    className="w-full rounded-full font-medium" 
    size="lg"
    disabled={loading}  // ← New
  >
    {loading ? 'Connecting...' : 'Connect with Knot'}  // ← New
  </Button>
)}
```

---

## 🧪 Testing Strategy

### Test Cases

1. **Happy Path**:
   - ✅ Login as demo user
   - ✅ Click "Connect with Knot"
   - ✅ See all 3 steps animate
   - ✅ Redirected to /accounts
   - ✅ See 1 linked account

2. **Error Handling**:
   - ✅ No internet: Show network error
   - ✅ Not logged in: Redirect to /login
   - ✅ Backend down: Show retry option

3. **Loading States**:
   - ✅ Button shows "Connecting..."
   - ✅ Steps animate properly
   - ✅ Cannot click button twice

### Console Output (Expected)

```
🔑 Token for /api/onboarding/start : eyJ...
🎯 Starting Knot onboarding...
✅ Session created: {session_id: "mock_session_1", sandbox_mode: true}
🔄 Step 1: Connecting...
🔄 Step 2: Granting permissions...
🔑 Token for /api/onboarding/complete : eyJ...
🎯 Completing onboarding...
✅ Onboarding complete: {success: true, accounts_linked: 1}
🔄 Step 3: Linked!
🎉 Linked 1 accounts
🚀 Redirecting to /accounts...
```

---

## 🚨 Risk Assessment

### Critical Risks (Must Avoid)
- ❌ Breaking existing login/signup flow: **AVOIDED** - Not touching those files
- ❌ Breaking existing API calls: **AVOIDED** - Only adding new methods
- ❌ UI regressions: **AVOIDED** - Preserving all existing components

### Medium Risks (Mitigated)
- ⚠️ Email not available: **MITIGATED** - Use getCurrentUser() API
- ⚠️ Backend down: **MITIGATED** - Graceful error handling
- ⚠️ Slow API: **MITIGATED** - Loading states + timeouts

### Low Risks (Acceptable)
- 🟢 User closes tab mid-flow: Natural behavior
- 🟢 Multiple clicks: Button disabled during loading

---

## 🎯 Success Criteria

### Must Have ✅
- [ ] Onboarding connects to real backend
- [ ] All 3 steps show and animate
- [ ] Errors display properly
- [ ] Loading states work
- [ ] Redirects to /accounts
- [ ] No console errors (except debug logs)
- [ ] No breaking changes to existing code

### Nice to Have 🎨
- [ ] Smooth error animations
- [ ] Retry functionality
- [ ] Toast notifications for success

---

## 📝 Implementation Checklist

### Pre-Implementation
- [x] Analyze existing code structure
- [x] Identify integration points
- [x] Create detailed plan
- [x] Review with user

### Implementation (30 mins)
- [ ] Add `startOnboarding` to api.ts
- [ ] Add `completeOnboarding` to api.ts
- [ ] Test API methods in browser console
- [ ] Update onboarding page imports
- [ ] Add state management (loading, error)
- [ ] Update `handleConnect` function
- [ ] Add error display component
- [ ] Update button with loading state
- [ ] Change redirect target to `/accounts`
- [ ] Get user email from API

### Testing (15 mins)
- [ ] Test happy path (login → onboard → accounts)
- [ ] Test error handling (disconnect internet)
- [ ] Test loading states
- [ ] Verify animations still work
- [ ] Check browser console for errors
- [ ] Verify accounts page shows linked account

### Verification
- [ ] No breaking changes
- [ ] All animations work
- [ ] Error handling works
- [ ] Backend mock mode works
- [ ] Ready for live mode (when credentials added)

---

## 🎨 Design Decisions

### 1. Where to get user email?
**Decision**: Call `api.getCurrentUser()` in `useEffect` on mount

**Rationale**: 
- ✅ Centralized user data
- ✅ Already authenticated
- ✅ No prop drilling needed

### 2. Redirect destination?
**Decision**: `/accounts` instead of `/chat/main`

**Rationale**:
- ✅ User just linked accounts, should see them
- ✅ More logical flow
- ✅ Matches backend completion behavior

### 3. Error recovery?
**Decision**: Show error + "Try Again" button

**Rationale**:
- ✅ User-friendly
- ✅ Doesn't break flow
- ✅ Allows recovery

### 4. Loading timing?
**Decision**: Keep similar timing (~4 seconds total)

**Rationale**:
- ✅ User expects animations
- ✅ Makes real API calls feel intentional
- ✅ Preserves UX

---

## 🔄 Rollback Plan

If something breaks:

1. **Revert api.ts changes**:
   ```bash
   git checkout frontend/lib/api.ts
   ```

2. **Revert onboarding page**:
   ```bash
   git checkout frontend/app/onboarding/page.tsx
   ```

3. **No other files affected** ✅

---

## 📚 Code Style Guide

### Follow Existing Patterns

1. **API Methods**:
   ```typescript
   async methodName(param: Type) {
     const response = await fetchWithAuth('/api/endpoint', {
       method: 'POST',
       body: JSON.stringify({ param }),
     })
     
     if (!response.ok) {
       if (response.status === 401 || response.status === 403) {
         return fallbackValue
       }
       const errorData = await response.json().catch(() => ({}))
       throw new Error(errorData.detail || 'Failed to ...')
     }
     
     return response.json()
   },
   ```

2. **Error Handling**:
   ```typescript
   try {
     // API call
   } catch (error) {
     console.error('Description:', error)
     setError(error.message || 'Generic message')
   }
   ```

3. **TypeScript**: Use existing type patterns from api.ts

---

## ✅ Ready to Implement

**Estimated Time**: 45 minutes total
- API methods: 10 mins
- Onboarding page: 20 mins
- Testing: 15 mins

**Risk Level**: 🟢 Low (well-planned, isolated changes)

**Backup Strategy**: ✅ Git revert available

**Next Step**: Implement Phase 1 (API methods)

---

**Status**: 📋 Plan Complete - Ready for Implementation

