"""Test script for write API endpoints."""
import httpx

BASE_URL = "http://localhost:8000"


def get_token():
    """Get authentication token."""
    login_data = {"email": "alice@demo.com", "password": "password123"}
    response = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5.0)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_write_endpoints():
    """Test all write API endpoints."""
    print("🧪 Testing Write API Endpoints...\n")
    
    # Get token
    print("🔑 Getting authentication token...")
    token = get_token()
    if not token:
        print("❌ Failed to get token. Make sure server is running.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Token obtained\n")
    
    # Test 1: POST message
    print("📝 Testing POST /api/chats/{chat_id}/messages...")
    try:
        message_data = {
            "content": "What's the best card for dining out?",
            "sender_type": "user"
        }
        response = httpx.post(
            f"{BASE_URL}/api/chats/1/messages",
            json=message_data,
            headers=headers,
            timeout=5.0
        )
        if response.status_code == 201:
            message = response.json()
            print(f"   ✅ Message created: ID {message['id']}")
            print(f"   📨 Content: {message['content']}")
            
            # Check if AI response was generated
            chat_response = httpx.get(f"{BASE_URL}/api/chats/1", headers=headers, timeout=5.0)
            if chat_response.status_code == 200:
                chat = chat_response.json()
                print(f"   🤖 Total messages in chat: {len(chat['messages'])}")
        else:
            print(f"   ⚠️  Returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: POST group
    print("\n👥 Testing POST /api/groups...")
    try:
        group_data = {
            "name": "Test Vacation Group",
            "members": ["alice@demo.com", "bob@test.com", "friend@example.com"]
        }
        response = httpx.post(
            f"{BASE_URL}/api/groups",
            json=group_data,
            headers=headers,
            timeout=5.0
        )
        if response.status_code == 201:
            group = response.json()
            print(f"   ✅ Group created: {group['name']}")
            print(f"   👤 Members: {len(group['members'])}")
            print(f"   💰 Total spend: ${group['total_spend']}")
        else:
            print(f"   ⚠️  Returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: DELETE account
    print("\n💳 Testing DELETE /api/accounts/{account_id}...")
    try:
        # Get current accounts first
        accounts_response = httpx.get(f"{BASE_URL}/api/accounts", headers=headers, timeout=5.0)
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
            if accounts_data["accounts"]:
                account_id = accounts_data["accounts"][0]["id"]
                account_name = accounts_data["accounts"][0]["institution"]
                
                response = httpx.delete(
                    f"{BASE_URL}/api/accounts/{account_id}",
                    headers=headers,
                    timeout=5.0
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Account deleted: {account_name}")
                    print(f"   📋 Message: {result['message']}")
                    
                    # Verify deletion
                    verify_response = httpx.get(f"{BASE_URL}/api/accounts", headers=headers, timeout=5.0)
                    if verify_response.status_code == 200:
                        remaining = verify_response.json()
                        print(f"   📊 Remaining accounts: {remaining['total']}")
                else:
                    print(f"   ⚠️  Returned: {response.status_code}")
            else:
                print("   ℹ️  No accounts to delete")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: PATCH settings
    print("\n⚙️  Testing PATCH /api/settings...")
    try:
        settings_data = {
            "section": "preferences",
            "data": {
                "notifications": {
                    "email": False,
                    "push": True
                }
            }
        }
        response = httpx.patch(
            f"{BASE_URL}/api/settings",
            json=settings_data,
            headers=headers,
            timeout=5.0
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Settings updated: {result['section']}")
            print(f"   📝 Message: {result['message']}")
            
            # Verify update
            verify_response = httpx.get(f"{BASE_URL}/api/settings", headers=headers, timeout=5.0)
            if verify_response.status_code == 200:
                settings = verify_response.json()
                notifications = settings["preferences"]["notifications"]
                print(f"   📧 Email notifications: {notifications.get('email')}")
                print(f"   📱 Push notifications: {notifications.get('push')}")
        else:
            print(f"   ⚠️  Returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n✅ All write endpoint tests complete!")
    print("\n📖 Visit http://localhost:8000/docs to try the API interactively")


if __name__ == "__main__":
    print("Make sure the server is running: make dev")
    print("=" * 60)
    test_write_endpoints()

