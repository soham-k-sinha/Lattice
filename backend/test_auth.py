"""Quick test script to verify authentication works."""
import httpx

BASE_URL = "http://localhost:8000"


def test_auth_flow():
    """Test the complete authentication flow."""
    print("🧪 Testing Authentication Flow...\n")
    
    # Test 1: Signup
    print("1️⃣ Testing Signup...")
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/auth/signup", json=signup_data, timeout=5.0)
        if response.status_code == 201:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   ✅ Signup successful! Token: {access_token[:20]}...")
        else:
            print(f"   ⚠️  Signup returned: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Signup failed: {e}")
        return
    
    # Test 2: Login with demo user
    print("\n2️⃣ Testing Login (demo user)...")
    login_data = {
        "email": "alice@demo.com",
        "password": "password123"
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=5.0)
        if response.status_code == 200:
            token_data = response.json()
            demo_token = token_data["access_token"]
            print(f"   ✅ Login successful! Token: {demo_token[:20]}...")
        else:
            print(f"   ⚠️  Login returned: {response.status_code}")
            demo_token = None
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        demo_token = None
    
    # Test 3: Get session
    if demo_token:
        print("\n3️⃣ Testing Session Endpoint...")
        headers = {"Authorization": f"Bearer {demo_token}"}
        
        try:
            response = httpx.get(f"{BASE_URL}/api/auth/session", headers=headers, timeout=5.0)
            if response.status_code == 200:
                session_data = response.json()
                print(f"   ✅ Session retrieved!")
                print(f"   User: {session_data['user']['name']} ({session_data['user']['email']})")
                print(f"   Authenticated: {session_data['authenticated']}")
            else:
                print(f"   ⚠️  Session returned: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Session check failed: {e}")
    
    # Test 4: Get user info
    if demo_token:
        print("\n4️⃣ Testing /me Endpoint...")
        headers = {"Authorization": f"Bearer {demo_token}"}
        
        try:
            response = httpx.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5.0)
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ User info retrieved!")
                print(f"   ID: {user_data['id']}")
                print(f"   Name: {user_data['name']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Onboarding: {user_data['onboarding_status']}")
            else:
                print(f"   ⚠️  /me returned: {response.status_code}")
        except Exception as e:
            print(f"   ❌ /me failed: {e}")
    
    # Test 5: Logout
    if demo_token:
        print("\n5️⃣ Testing Logout...")
        headers = {"Authorization": f"Bearer {demo_token}"}
        
        try:
            response = httpx.post(f"{BASE_URL}/api/auth/logout", headers=headers, timeout=5.0)
            if response.status_code == 200:
                print(f"   ✅ Logout successful!")
            else:
                print(f"   ⚠️  Logout returned: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Logout failed: {e}")
    
    print("\n✅ Authentication flow test complete!")


if __name__ == "__main__":
    print("Make sure the server is running: make dev")
    print("=" * 50)
    test_auth_flow()

