"""Test script for all API endpoints."""
import httpx

BASE_URL = "http://localhost:8000"


def get_token():
    """Get authentication token."""
    login_data = {"email": "alice@demo.com", "password": "password123"}
    response = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5.0)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_all_endpoints():
    """Test all API endpoints."""
    print("🧪 Testing All API Endpoints...\n")
    
    # Get token
    print("🔑 Getting authentication token...")
    token = get_token()
    if not token:
        print("❌ Failed to get token. Make sure server is running.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Token obtained: {token[:20]}...\n")
    
    # Test chats
    print("💬 Testing Chats API...")
    try:
        response = httpx.get(f"{BASE_URL}/api/chats", headers=headers, timeout=5.0)
        if response.status_code == 200:
            chats = response.json()
            print(f"   ✅ GET /api/chats: {len(chats)} chats returned")
        
        # Get specific chat
        response = httpx.get(f"{BASE_URL}/api/chats/1", headers=headers, timeout=5.0)
        if response.status_code == 200:
            chat = response.json()
            print(f"   ✅ GET /api/chats/1: {len(chat.get('messages', []))} messages")
    except Exception as e:
        print(f"   ❌ Chats API failed: {e}")
    
    # Test groups
    print("\n👥 Testing Groups API...")
    try:
        response = httpx.get(f"{BASE_URL}/api/groups", headers=headers, timeout=5.0)
        if response.status_code == 200:
            groups = response.json()
            print(f"   ✅ GET /api/groups: {len(groups)} groups returned")
        
        # Get specific group
        response = httpx.get(f"{BASE_URL}/api/groups/2", headers=headers, timeout=5.0)
        if response.status_code == 200:
            group = response.json()
            print(f"   ✅ GET /api/groups/2: {group.get('name')}")
    except Exception as e:
        print(f"   ❌ Groups API failed: {e}")
    
    # Test accounts
    print("\n💳 Testing Accounts API...")
    try:
        response = httpx.get(f"{BASE_URL}/api/accounts", headers=headers, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ GET /api/accounts: {data.get('total')} accounts")
        
        response = httpx.get(f"{BASE_URL}/api/accounts/status", headers=headers, timeout=5.0)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ GET /api/accounts/status: {status_data.get('connected')}")
    except Exception as e:
        print(f"   ❌ Accounts API failed: {e}")
    
    # Test insights
    print("\n📊 Testing Insights API...")
    try:
        response = httpx.get(f"{BASE_URL}/api/insights", headers=headers, timeout=5.0)
        if response.status_code == 200:
            insights = response.json()
            print(f"   ✅ GET /api/insights: {len(insights.get('cards', []))} card insights")
            print(f"                        {len(insights.get('trends', []))} spending trends")
        
        response = httpx.get(f"{BASE_URL}/api/insights/summary", headers=headers, timeout=5.0)
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✅ GET /api/insights/summary: {summary.get('month')}")
    except Exception as e:
        print(f"   ❌ Insights API failed: {e}")
    
    # Test settings
    print("\n⚙️  Testing Settings API...")
    try:
        response = httpx.get(f"{BASE_URL}/api/settings", headers=headers, timeout=5.0)
        if response.status_code == 200:
            settings_data = response.json()
            print(f"   ✅ GET /api/settings: {settings_data.get('account', {}).get('name')}")
            print(f"                        Theme: {settings_data.get('preferences', {}).get('display', {}).get('theme')}")
    except Exception as e:
        print(f"   ❌ Settings API failed: {e}")
    
    print("\n✅ All endpoint tests complete!")
    print("\n📖 Visit http://localhost:8000/docs to explore the API interactively")


if __name__ == "__main__":
    print("Make sure the server is running: make dev")
    print("=" * 60)
    test_all_endpoints()

