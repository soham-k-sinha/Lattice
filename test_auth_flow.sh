#!/bin/bash

# Test Authentication Flow
# This script tests the complete auth flow from backend

set -e

echo "🧪 Testing Lattice Authentication Flow"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

# Test 1: Health Check
echo "📋 Test 1: Backend Health Check"
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi
echo ""

# Test 2: Login and get token
echo "📋 Test 2: Login with Demo Credentials"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@demo.com", "password": "password123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✅ Login successful${NC}"
    echo "   Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Access protected endpoint with token
echo "📋 Test 3: Fetch Chats (Protected Endpoint)"
CHATS=$(curl -s "$API_URL/api/chats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$CHATS" | grep -q "id"; then
    echo -e "${GREEN}✅ Successfully fetched chats${NC}"
    echo "   Found chats: $(echo "$CHATS" | grep -o '"id"' | wc -l | tr -d ' ')"
else
    echo -e "${RED}❌ Failed to fetch chats${NC}"
    echo "   Response: $CHATS"
    exit 1
fi
echo ""

# Test 4: Access protected endpoint without token
echo "📋 Test 4: Fetch Chats Without Token (Should Fail)"
UNAUTH=$(curl -s "$API_URL/api/chats" \
  -H "Content-Type: application/json")

if echo "$UNAUTH" | grep -q "Not authenticated"; then
    echo -e "${GREEN}✅ Correctly rejected unauthenticated request${NC}"
else
    echo -e "${RED}❌ Security issue: Unauthenticated request succeeded${NC}"
    exit 1
fi
echo ""

# Test 5: Get user info
echo "📋 Test 5: Get Current User Info"
USER=$(curl -s "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$USER" | grep -q "alice@demo.com"; then
    echo -e "${GREEN}✅ Successfully fetched user info${NC}"
    echo "   User: $(echo "$USER" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)"
else
    echo -e "${RED}❌ Failed to fetch user info${NC}"
    echo "   Response: $USER"
    exit 1
fi
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}🎉 All authentication tests passed!${NC}"
echo ""
echo "📝 Summary:"
echo "   ✅ Backend is healthy"
echo "   ✅ Login works and returns token"
echo "   ✅ Token authenticates protected endpoints"
echo "   ✅ Requests without token are rejected"
echo "   ✅ User info retrieval works"
echo ""
echo "💡 Next steps:"
echo "   1. Open browser to http://localhost:3000/login"
echo "   2. Open DevTools Console (F12)"
echo "   3. Login with: alice@demo.com / password123"
echo "   4. Check console for debug logs (🔑, ✅, 🔀)"
echo "   5. Should redirect to /chat/1 without errors"
echo ""

