# Authentication Error Fix

## Problem

When visiting the application without being logged in, the following error appeared in the browser console:

```
[Error] Failed to load chats: – Error: Failed to fetch chats — api.ts:103
```

This error occurred when the `ChatSidebar` component attempted to fetch chats from the backend API, which requires authentication.

## Root Cause

1. The `ChatSidebar` component calls `api.getChats()` on mount (via `useEffect`)
2. If the user is not logged in (no `access_token` in localStorage), the backend returns a `401 Unauthorized` response
3. The `fetchWithAuth` function in `api.ts` correctly redirects to `/login` on 401 errors
4. However, the API methods were still throwing errors after the redirect was triggered
5. This caused error messages to appear in the console before the redirect completed

## Solution

Updated all API methods in `frontend/lib/api.ts` to handle 401 errors gracefully:

### For GET methods (fetching data):
- Return empty data structures (empty arrays, empty objects) when receiving a 401
- Allow the `fetchWithAuth` function to handle the redirect to `/login`
- Prevent error messages from appearing in the console

### For POST/DELETE methods (mutating data):
- Throw an error for 401 to prevent the operation from appearing to succeed
- The `fetchWithAuth` function will still redirect to `/login`

### Improved error messages:
- Extract the `detail` field from backend error responses when available
- Provide more informative error messages to users
- Use `.catch()` when parsing error JSON to handle non-JSON error responses

## Changes Made

### Updated `api.ts` methods:
- `getChats()` - Returns `[]` on 401
- `getChat()` - Returns `{ id, messages: [] }` on 401
- `sendMessage()` - Throws error on 401
- `getGroups()` - Returns `[]` on 401
- `getGroup()` - Returns `{ id, name: '', members: [] }` on 401
- `getAccounts()` - Returns `[]` on 401
- `getAccountsStatus()` - Returns `{ connected: false, total: 0 }` on 401
- `getInsights()` - Returns `[]` on 401
- `getSettings()` - Returns `{}` on 401

### Updated `chat-sidebar.tsx`:
- Added comment explaining that `fetchWithAuth` handles 401 redirects
- No functional changes needed as the error handling already exists

## Testing

To verify the fix:

1. **Logged out state**: Visit any authenticated page (e.g., `/chat/1`) without being logged in
   - Expected: Automatically redirected to `/login` without console errors
   
2. **Logged in state**: Log in and use the application normally
   - Expected: All API calls work as before
   
3. **Expired token**: If token expires during a session
   - Expected: Next API call redirects to `/login` without console errors

## Benefits

1. **Better UX**: No confusing error messages in the console
2. **Cleaner code**: Consistent error handling across all API methods
3. **More informative errors**: Backend error details are now shown to users
4. **Graceful degradation**: App handles authentication failures smoothly

## Authentication Flow

```
User visits authenticated page
  ↓
Component calls API method (e.g., getChats())
  ↓
fetchWithAuth checks for access_token in localStorage
  ↓
If no token or invalid token → Backend returns 401
  ↓
fetchWithAuth redirects to /login
  ↓
API method returns empty data (no error thrown)
  ↓
Component renders empty state until redirect completes
```

## Notes

- The `fetchWithAuth` function already handles token removal and redirect on 401
- The fix ensures errors don't propagate to the console during the redirect
- For POST/DELETE operations, we still throw errors to prevent silent failures
- This pattern can be applied to any new API methods added in the future

