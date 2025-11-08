# Frontend Knot Integration Guide

## 🎯 Goal

Connect your frontend to the Knot endpoints to test the complete onboarding flow.

**Time**: 1-2 hours  
**Mode**: Mock (no real Knot credentials needed)

---

## Step 1: Add API Methods (5 mins)

**File: `frontend/lib/api.ts`**

Add these two methods after the `logout()` method:

```typescript
// ============= Onboarding (Knot Integration) =============

async startOnboarding(email: string, phone?: string) {
  const response = await fetchWithAuth('/api/onboarding/start', {
    method: 'POST',
    body: JSON.stringify({ email, phone }),
  })

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error('Not authenticated')
    }
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to start onboarding')
  }

  return response.json()
},

async completeOnboarding(sessionId: string) {
  const response = await fetchWithAuth('/api/onboarding/complete', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error('Not authenticated')
    }
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to complete onboarding')
  }

  return response.json()
},
```

---

## Step 2: Update Onboarding Page (30 mins)

**File: `frontend/app/onboarding/page.tsx`**

Find the "Connect with Knot" button handler and update it:

```typescript
const [loading, setLoading] = useState(false)
const [error, setError] = useState('')

const handleKnotConnect = async () => {
  setLoading(true)
  setError('')
  
  try {
    // 1. Start onboarding (get session token)
    console.log('🔐 Starting Knot onboarding...')
    const startResult = await api.startOnboarding('demo@example.com')
    console.log('✅ Session created:', startResult)
    
    if (startResult.sandbox_mode) {
      console.log('📦 Running in mock mode')
    }
    
    // 2. TODO: In production, initialize Knot SDK here
    // const knot = new KnotSDK({ sessionToken: startResult.session_token })
    // await knot.open()
    // User completes linking in Knot SDK
    
    // 3. Complete onboarding (fetch linked accounts)
    console.log('📡 Completing onboarding...')
    const completeResult = await api.completeOnboarding(startResult.session_id)
    console.log('✅ Onboarding complete:', completeResult)
    console.log(`🎉 Linked ${completeResult.accounts_linked} accounts`)
    
    // 4. Redirect to accounts page
    router.push('/accounts')
    
  } catch (error: any) {
    console.error('❌ Knot connection failed:', error)
    setError(error.message || 'Failed to connect accounts')
  } finally {
    setLoading(false)
  }
}
```

Add error display in the UI:

```typescript
{error && (
  <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
    {error}
  </div>
)}

<Button 
  onClick={handleKnotConnect}
  disabled={loading}
  className="w-full"
>
  {loading ? 'Connecting...' : 'Connect with Knot'}
</Button>
```

---

## Step 3: Test the Flow (15 mins)

### Start Backend
```bash
cd backend
poetry run python run.py
```

### Start Frontend
```bash
cd frontend
npm run dev  # or pnpm dev
```

### Test Steps

1. **Login**: Go to http://localhost:3000/login
   - Email: `alice@demo.com`
   - Password: `password123`

2. **Navigate to Onboarding**: http://localhost:3000/onboarding

3. **Click "Connect with Knot"**

4. **Watch Browser Console** (F12):
   ```
   🔐 Starting Knot onboarding...
   ✅ Session created: {session_token: "mock_token_1", ...}
   📦 Running in mock mode
   📡 Completing onboarding...
   ✅ Onboarding complete: {success: true, accounts_linked: 1}
   🎉 Linked 1 accounts
   ```

5. **Verify Redirect**: Should go to `/accounts`

6. **Check Accounts Page**: Should show 1 linked Amazon account

---

## Step 4: Verify Accounts Page (5 mins)

Visit http://localhost:3000/accounts

You should see:
- ✅ Amazon account listed
- ✅ Last synced timestamp
- ✅ "Sandbox Mode Active" banner

---

## 🎉 Success Criteria

- [ ] Can click "Connect with Knot" button
- [ ] See console logs showing the flow
- [ ] Get redirected to /accounts
- [ ] See linked Amazon account
- [ ] No errors in console
- [ ] Loading states work correctly

---

## 🐛 Troubleshooting

### "Not authenticated" error

**Fix**: Make sure you're logged in first at `/login`

### "Failed to start onboarding"

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. Token exists: Check localStorage in browser console
3. Backend logs: Check terminal for errors

### Accounts page shows no accounts

**Fix**: 
1. Make sure you completed BOTH steps (start + complete)
2. Check browser console for errors
3. Refresh the accounts page

### Still seeing mock data on accounts page

**This is correct!** Mock mode is working. You should see:
- 1 Amazon account
- "Sandbox Mode Active" banner

---

## 🚀 Next: Switch to Live Mode

Once frontend integration works, you can switch to live Knot:

1. Get Knot credentials from https://knotapi.com
2. Update `backend/.env`:
   ```bash
   FEATURE_KNOT=true
   KNOT_CLIENT_ID=your_id
   KNOT_CLIENT_SECRET=your_secret
   ```
3. Restart backend
4. Test again - now it will use real Knot API!

---

## 📊 API Flow Summary

```
Frontend                    Backend                     Knot API
   |                           |                            |
   | POST /api/onboarding/start |                           |
   |--------------------------->|                            |
   |                           | (Mock: return fake token)  |
   |                           | (Live: POST /session/create) -> |
   |<--------------------------|                            |
   | {session_token, session_id}                           |
   |                           |                            |
   | [User would use Knot SDK here in production]         |
   |                           |                            |
   | POST /api/onboarding/complete                         |
   |--------------------------->|                            |
   |                           | (Mock: create fake account)|
   |                           | (Live: GET /accounts/get)  -> |
   |<--------------------------|                            |
   | {success, accounts_linked: 1}                         |
   |                           |                            |
   | Navigate to /accounts     |                            |
   |                           |                            |
   | GET /api/accounts         |                            |
   |--------------------------->|                            |
   |<--------------------------|                            |
   | {accounts: [...]}         |                            |
```

---

## ✅ Checklist

Integration Steps:
- [ ] Added `startOnboarding()` to api.ts
- [ ] Added `completeOnboarding()` to api.ts
- [ ] Updated onboarding page handler
- [ ] Added error handling
- [ ] Added loading states
- [ ] Tested complete flow
- [ ] Verified accounts page shows data

Ready for live mode!

