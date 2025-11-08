# 🔧 Troubleshooting "Not authenticated" Error

## The Problem
You're getting `{"detail": "Not authenticated"}` when trying to send messages or create groups.

## Quick Fixes (Try These First)

### Fix 1: Login Again
1. Go to http://localhost:3000
2. If you're on any page, click logout (or go to /login)
3. Login with:
   - Email: `alice@demo.com`
   - Password: `password123`
4. Try your action again

### Fix 2: Clear & Re-login
1. Open browser console (F12)
2. Type: `localStorage.clear()`
3. Press Enter
4. Refresh the page
5. Login again
6. Try your action

### Fix 3: Check Token
1. Open browser console (F12)
2. Type: `localStorage.getItem('access_token')`
3. Press Enter

**If you see:**
- `null` → You're not logged in! Go to /login
- A long string like `"eyJhbGc..."` → Token exists, continue to next section

---

## Deep Dive: What's Happening

### When You Login
```
1. You enter email/password
2. Frontend calls: POST /api/auth/login
3. Backend returns: { "access_token": "eyJhbGc..." }
4. Frontend saves to: localStorage.setItem('access_token', token)
```

### When You Send Message/Create Group
```
1. Frontend reads: localStorage.getItem('access_token')
2. Frontend sends: Authorization: Bearer eyJhbGc...
3. Backend checks: Is this token valid?
4. If valid: ✅ Action succeeds
5. If invalid/missing: ❌ "Not authenticated"
```

---

## Manual Test in Browser Console

Open console (F12) and paste this:

```javascript
// Step 1: Check if you have a token
const token = localStorage.getItem('access_token');
console.log('Token:', token ? token.substring(0, 30) + '...' : 'NO TOKEN!');

// Step 2: If no token, login
if (!token) {
    console.log('❌ No token found. Please login first!');
} else {
    // Step 3: Test if token works
    fetch('http://localhost:8000/api/chats', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(r => {
        console.log('Response status:', r.status);
        return r.json();
    })
    .then(data => {
        if (data.detail) {
            console.log('❌ Error:', data.detail);
        } else {
            console.log('✅ Success! Chats:', data);
        }
    })
    .catch(e => console.log('❌ Network error:', e));
}
```

---

## Expected Results

### If Not Logged In
```javascript
Token: NO TOKEN!
❌ No token found. Please login first!
```
**Fix:** Go to /login and login

### If Token Expired/Invalid
```javascript
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
Response status: 401
❌ Error: Not authenticated
```
**Fix:** `localStorage.clear()` then login again

### If Everything Works
```javascript
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
Response status: 200
✅ Success! Chats: [{...}, {...}]
```
**Fix:** Nothing! It's working. The issue is elsewhere.

---

## Common Causes & Solutions

### Cause 1: Never Logged In
**Symptoms:** 
- Went directly to /chat/1 without logging in
- Refreshed page after server restart

**Solution:**
```
Visit http://localhost:3000/login
Login with alice@demo.com / password123
```

### Cause 2: Server Restarted
**Symptoms:**
- Was working before
- Stopped working after restarting backend

**Solution:**
```
Backend restart doesn't affect tokens!
Just refresh the browser and it should work.
```

### Cause 3: localStorage Cleared
**Symptoms:**
- Cleared browser data
- Used incognito mode
- Different browser

**Solution:**
```
Just login again - that's it!
```

### Cause 4: Wrong URL/Port
**Symptoms:**
- API calls go to wrong port
- CORS errors in console

**Solution:**
```
Backend should be on: http://localhost:8000
Frontend should be on: http://localhost:3000
```

---

## Step-by-Step Login Process

### 1. Start Both Servers
```bash
# Terminal 1 - Backend
cd backend
make dev

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 2. Visit Frontend
```
http://localhost:3000
```

### 3. Click "Get Started"
Should redirect to `/login`

### 4. Enter Credentials
```
Email: alice@demo.com
Password: password123
```

### 5. Click "Sign In"
Should see loading, then redirect to `/chat/1`

### 6. Verify Token
Open console (F12), type:
```javascript
localStorage.getItem('access_token')
```
Should see a long string

### 7. Try Actions
- Send a message → Should work
- Create a group → Should work
- View accounts → Should work

---

## Still Not Working?

If you followed all steps and still get "Not authenticated":

### Check Backend Logs
Look at your backend terminal. When you try to send a message, you should see:
```
INFO:     127.0.0.1:xxxxx - "POST /api/chats/1/messages HTTP/1.1" 201 Created
```

If you see:
```
INFO:     127.0.0.1:xxxxx - "POST /api/chats/1/messages HTTP/1.1" 403 Forbidden
```

Then the backend isn't recognizing the token.

### Test Backend Directly
```bash
cd backend
poetry run python test_write_api.py
```

Should show all green ✅

If backend tests pass but browser fails:
- It's a frontend issue
- Check browser console for errors
- Check Network tab for failed requests

---

## Debug Commands

Run these in browser console (F12):

```javascript
// 1. Check token
console.log('Token:', localStorage.getItem('access_token'));

// 2. Test login
fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'alice@demo.com',
        password: 'password123'
    })
})
.then(r => r.json())
.then(data => {
    console.log('Login response:', data);
    if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        console.log('✅ Token saved! Refresh the page.');
    }
});

// 3. Test protected endpoint
const token = localStorage.getItem('access_token');
fetch('http://localhost:8000/api/chats/1/messages', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        content: 'Test from console',
        sender_type: 'user'
    })
})
.then(r => {
    console.log('Status:', r.status);
    return r.json();
})
.then(data => console.log('Response:', data));
```

---

## Quick Recovery

If nothing works, **full reset**:

```bash
# 1. Stop both servers (Ctrl+C in both terminals)

# 2. Restart backend
cd backend
make dev

# 3. Restart frontend
cd frontend
npm run dev

# 4. Clear browser
# Open console (F12)
localStorage.clear()
# Refresh page (F5)

# 5. Login
# Go to http://localhost:3000/login
# Login with alice@demo.com / password123

# 6. Try again
```

---

## Contact for Help

If still stuck, provide:
1. ✅ Backend terminal output (last 20 lines)
2. ✅ Browser console errors (screenshot)
3. ✅ Network tab failed requests (screenshot)
4. ✅ Result of: `localStorage.getItem('access_token')` in console
5. ✅ Result of backend test: `poetry run python test_write_api.py`

