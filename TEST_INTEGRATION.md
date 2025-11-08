# 🧪 Frontend-Backend Integration Test Guide

## Quick Start Test

### 1. Start Both Servers

```bash
# Terminal 1: Backend
cd backend
make dev

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Open Browser
Visit: http://localhost:3000

---

## ✅ Integration Test Checklist

### Test 1: Landing → Login
- [ ] Landing page loads
- [ ] Animated background renders
- [ ] Click "Get Started"
- [ ] Redirects to `/login`
- [ ] Login form appears

### Test 2: Authentication
- [ ] Enter `alice@demo.com`
- [ ] Enter `password123`
- [ ] Click "Sign In"
- [ ] Redirects to `/chat/1`
- [ ] Chat page loads with messages

### Test 3: Chat Functionality
- [ ] See existing messages from backend
- [ ] Type: "What's the best card?"
- [ ] Press Enter
- [ ] Your message appears
- [ ] Loading spinner shows
- [ ] AI response appears (1-2 seconds)
- [ ] AI response includes thinking steps

### Test 4: Chat Sidebar
- [ ] Click hamburger/toggle to open sidebar
- [ ] See list of chats (loaded from backend)
- [ ] Chat titles visible
- [ ] Last messages visible
- [ ] Click different chat to navigate

### Test 5: Groups Page
- [ ] Navigate to Groups (via nav)
- [ ] See list of groups
- [ ] Member counts shown
- [ ] Total spend shown
- [ ] Click "Create Group"

### Test 6: Create Group
- [ ] Dialog opens
- [ ] Enter group name: "Test Group"
- [ ] Add email: "test1@example.com"
- [ ] Add email: "test2@example.com"
- [ ] Click "Create Group"
- [ ] New group appears in list
- [ ] Redirect to groups page

### Test 7: Accounts Page
- [ ] Navigate to Accounts
- [ ] See list of accounts
- [ ] Account details visible (institution, balance)
- [ ] Click trash icon on account
- [ ] Confirm deletion
- [ ] Account disappears
- [ ] Remaining accounts count updates

### Test 8: Insights Page
- [ ] Navigate to Insights
- [ ] See list of insights
- [ ] Different insight types shown
- [ ] Monthly summary at bottom
- [ ] Impact values visible

### Test 9: Settings Page
- [ ] Navigate to Settings
- [ ] User profile card visible
- [ ] Name and email shown
- [ ] Connected accounts count correct
- [ ] Preferences displayed
- [ ] Click "Sign Out"

### Test 10: Logout
- [ ] Redirects to `/login`
- [ ] Try accessing `/chat/1` directly
- [ ] Should redirect back to login
- [ ] Token cleared from localStorage

---

## 🔍 Console Checks

### Open Browser Console (F12)

**Should NOT see:**
- ❌ CORS errors
- ❌ 404 errors
- ❌ Network errors
- ❌ Unhandled promise rejections

**Should see:**
- ✅ Successful API calls to `localhost:8000`
- ✅ 200 OK responses
- ✅ Data logged (optional debug logs)

---

## 🧪 API Test (Direct Backend)

### Terminal Test
```bash
# Test backend directly
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@demo.com","password":"password123"}'
# Expected: {"access_token":"...","token_type":"bearer"}

# Test protected endpoint (use token from above)
TOKEN="your_token_here"
curl http://localhost:8000/api/chats \
  -H "Authorization: Bearer $TOKEN"
# Expected: Array of chats
```

---

## 🎯 Expected Results

### Backend Running
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started server process
INFO:     Application startup complete.
```

### Frontend Running
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in X.Xs
```

### Browser Network Tab
- Should see requests to `http://localhost:8000/api/*`
- All should return 200 (except 401 if not logged in)
- Responses should contain JSON data

---

## ⚠️ Troubleshooting

### Problem: "Failed to fetch"
**Solution:**
- Check backend is running
- Check URL is `http://localhost:8000` (not https)
- Check CORS is enabled in backend

### Problem: "401 Unauthorized"
**Solution:**
- Log out and log back in
- Check token in localStorage (F12 → Application → Local Storage)
- Clear localStorage and try again

### Problem: "Network Error"
**Solution:**
- Ensure both servers are running
- Check firewall isn't blocking ports
- Try different browser

### Problem: Page shows loading forever
**Solution:**
- Check console for errors
- Check backend logs for errors
- Refresh page
- Clear cache and try again

---

## ✅ Success Criteria

All of the following should work:

1. ✅ Login with demo credentials
2. ✅ See real chats from backend
3. ✅ Send message and get AI response
4. ✅ Create new group
5. ✅ Delete account
6. ✅ View insights
7. ✅ Logout successfully
8. ✅ Protected routes redirect to login

---

## 📊 Performance Expectations

### Page Load Times
- Landing: < 1s
- Login: < 1s
- Chat (with data): < 2s
- Groups: < 1s
- Accounts: < 1s
- Insights: < 2s
- Settings: < 1s

### API Response Times
- Login: < 500ms
- Get Chats: < 200ms
- Send Message: < 1s (includes AI response generation)
- Create Group: < 300ms
- Delete Account: < 200ms

---

## 🎉 Integration Complete When...

- [ ] All 10 tests pass
- [ ] No console errors
- [ ] All API calls succeed
- [ ] Data loads correctly
- [ ] Actions work (send, create, delete)
- [ ] Authentication flow works
- [ ] Logout works
- [ ] Protected routes redirect

---

**If all checks pass: 🎉 YOUR INTEGRATION IS PERFECT!**

Visit the full documentation: `FRONTEND_BACKEND_INTEGRATION.md`

