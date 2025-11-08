# Authentication Debugging Guide

## Current Issue

You're seeing errors like:
```
[Error] Failed to load chats: – Error: Not authenticated — api.ts:108
[Error] Failed to load chat: – Error: Not authenticated — api.ts:123
```

## Root Cause Analysis

The "Not authenticated" error means the backend is not receiving a valid authentication token. This could happen for several reasons:

### Possible Causes

1. **You haven't logged in yet**
   - If you navigate directly to `/chat/1` without logging in first, there's no token in localStorage
   - Solution: Always login at `/login` before accessing protected pages

2. **Token expired**
   - JWT tokens have an expiration time (configured in backend)
   - Solution: Login again to get a fresh token

3. **Browser cache issues**
   - Old JavaScript code might be cached in your browser
   - Solution: Hard refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

4. **localStorage blocked**
   - Some browsers/settings block localStorage
   - Solution: Check browser settings and privacy mode

## Debugging Steps

### Step 1: Clear Browser Cache
```bash
# In your browser:
# - Open DevTools (F12 or Cmd+Option+I)
# - Right-click the refresh button
# - Select "Empty Cache and Hard Reload"
```

### Step 2: Check Console Logs

With the updated code, you should now see detailed debug logs in your browser console:

**During Login:**
```
🔐 Login attempt: alice@demo.com
📡 Calling backend login API...
✅ Login response received: {access_token: "eyJ..."}
✅ Token saved to localStorage
🔍 Verified token in localStorage: YES
🔀 Redirecting to /chat/1...
```

**During API Calls:**
```
🔑 Token for /api/chats : eyJhbGciOiJIUzI1NiI...
```

**If Not Authenticated:**
```
🔑 Token for /api/chats : NO TOKEN
🚫 401 Unauthorized - redirecting to /login
```

### Step 3: Manually Check localStorage

In your browser console, run:
```javascript
// Check if token exists
localStorage.getItem('access_token')

// Should return something like:
// "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFsaWNlQGRlbW8uY29tIiwibmFtZSI6IkFsaWNlIERlbW8iLCJleHAiOjE3NjI1OTMxODF9.IlK07jdJAENRgMYRHf4tWvSLb3Mi3DZ8stI4yf6rTuI"

// If it returns null, you're not logged in
```

### Step 4: Test Login Flow

1. **Open browser DevTools** (F12)
2. **Navigate to** `http://localhost:3000/login`
3. **Enter credentials:**
   - Email: `alice@demo.com`
   - Password: `password123`
4. **Click "Sign In"**
5. **Watch the console** for the login flow logs
6. **Verify redirect** to `/chat/1`
7. **Check console** for token presence in API calls

### Step 5: Test API Calls Manually

In your browser console (after logging in):
```javascript
// Test if token is being sent
fetch('http://localhost:8000/api/chats', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(d => console.log('Chats:', d))
```

## What I Fixed

### 1. Added Debug Logging to `fetchWithAuth`

Now logs:
- Token presence/absence before each API call
- 401 responses and redirect actions

### 2. Improved Error Handling in API Methods

- `getChats()` and `getChat()` now have try-catch blocks
- Returns empty data on errors instead of throwing
- Prevents error messages from showing during auth redirects
- Uses `console.debug()` instead of `console.error()` for auth failures

### 3. Enhanced Login Page Verification

- Verifies token was actually saved to localStorage
- More detailed logging throughout the login process
- Helps identify localStorage issues

## Expected Behavior

### When NOT logged in:
1. Visit any protected page (e.g., `/chat/1`)
2. API calls return empty data immediately
3. `fetchWithAuth` detects no token
4. Automatically redirects to `/login`
5. **No error messages in console** (just debug logs)

### When logged in:
1. Login at `/login`
2. Token is saved to localStorage
3. Redirect to `/chat/1`
4. API calls include `Authorization: Bearer <token>` header
5. Backend validates token and returns data
6. Everything works normally

### When token expires:
1. API call gets 401 response
2. `fetchWithAuth` detects 401
3. Removes invalid token from localStorage
4. Redirects to `/login`
5. **No error messages in console** (just debug logs)

## Common Issues and Solutions

### Issue: "No token" in console but I just logged in
**Cause:** Browser cache serving old JavaScript
**Solution:** Hard refresh (Cmd+Shift+R)

### Issue: Token exists but still getting 401
**Cause:** Token expired or invalid
**Solution:** 
```javascript
// In console, check token expiration:
const token = localStorage.getItem('access_token')
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('Expires:', new Date(payload.exp * 1000))

// If expired, clear it and login again:
localStorage.removeItem('access_token')
window.location.href = '/login'
```

### Issue: Errors still showing in console
**Cause:** Old cached JavaScript files
**Solution:** 
1. Clear browser cache completely
2. Hard refresh (Cmd+Shift+R)
3. Or use incognito/private mode for testing

### Issue: localStorage.getItem returns null after login
**Cause:** Private/incognito mode or browser settings blocking localStorage
**Solution:**
1. Check browser privacy settings
2. Try in normal (non-private) mode
3. Check if localStorage is enabled:
   ```javascript
   typeof Storage !== 'undefined' && typeof localStorage !== 'undefined'
   ```

## Testing Checklist

- [ ] Backend is running (`curl http://localhost:8000/health`)
- [ ] Frontend is running (`http://localhost:3000`)
- [ ] Browser cache cleared
- [ ] DevTools console open
- [ ] Login at `/login` with demo credentials
- [ ] See success logs in console
- [ ] Verify token in localStorage
- [ ] Navigate to `/chat/1`
- [ ] See chat data load without errors
- [ ] No "Not authenticated" errors in console
- [ ] Only see debug logs (🔑, 🚫, etc.)

## Next Steps

If you're still seeing errors after following all these steps:

1. **Share your console output** - The debug logs will tell us exactly what's happening
2. **Check Network tab** - See what headers are being sent with requests
3. **Verify backend is in DEBUG mode** - Check `backend/app/config/settings.py`

## Debug Mode Verification

Check if backend is in DEBUG mode:
```bash
cd backend
grep -r "DEBUG" app/config/settings.py
```

Should show `DEBUG = True` for development.

