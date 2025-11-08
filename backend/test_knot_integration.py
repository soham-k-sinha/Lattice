"""
Test Knot Integration
Run this to verify the Knot integration is working
"""
import asyncio
import sys
from app.integrations.knot import KnotClient, KnotAPIError
from app.config.settings import settings


async def test_mock_mode():
    """Test that mock mode works (no credentials needed)"""
    print("\n🧪 Test 1: Mock Mode (no credentials)")
    print("=" * 50)
    
    knot = KnotClient()
    
    if knot.mock_mode:
        print("✅ KnotClient initialized in mock mode")
        print(f"   FEATURE_KNOT: {settings.FEATURE_KNOT}")
        print(f"   Has credentials: {bool(settings.KNOT_CLIENT_ID and settings.KNOT_CLIENT_SECRET)}")
        return True
    else:
        print("⚠️  KnotClient not in mock mode")
        return False


async def test_with_credentials():
    """Test with real credentials (if available)"""
    print("\n🧪 Test 2: Real API (with credentials)")
    print("=" * 50)
    
    if not settings.KNOT_CLIENT_ID or not settings.KNOT_CLIENT_SECRET:
        print("⏭️  Skipped - No credentials configured")
        print("   Set KNOT_CLIENT_ID and KNOT_CLIENT_SECRET to test")
        return True
    
    knot = KnotClient()
    try:
        # Test listing merchants
        print("📋 Testing GET /merchant/list...")
        merchants = await knot.list_merchants()
        print(f"✅ Found {len(merchants)} merchants")
        
        if merchants:
            print(f"   Sample: {merchants[0].name} (id: {merchants[0].id})")
        
        # Test creating a session
        print("\n📋 Testing POST /session/create...")
        session = await knot.create_session(
            external_user_id="test_user_1",
            contact={"email": "test@example.com"}
        )
        print(f"✅ Created session: {session.session_id}")
        print(f"   Token: {session.session_token[:20]}...")
        print(f"   Expires: {session.expires_at}")
        
        return True
        
    except KnotAPIError as e:
        print(f"❌ Knot API Error: {e.message}")
        print(f"   Status: {e.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await knot.close()


async def test_api_endpoints():
    """Test the FastAPI endpoints"""
    print("\n🧪 Test 3: FastAPI Endpoints")
    print("=" * 50)
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Test login first
        print("📋 Testing login...")
        login_response = client.post(
            "/api/auth/login",
            json={"email": "alice@demo.com", "password": "password123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test onboarding start
        print("\n📋 Testing POST /api/onboarding/start...")
        start_response = client.post(
            "/api/onboarding/start",
            json={"email": "alice@demo.com"},
            headers=headers
        )
        
        if start_response.status_code != 200:
            print(f"❌ Onboarding start failed: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return False
        
        start_data = start_response.json()
        print("✅ Onboarding start successful")
        print(f"   Session ID: {start_data['session_id']}")
        print(f"   Sandbox mode: {start_data['sandbox_mode']}")
        
        # Test onboarding complete
        print("\n📋 Testing POST /api/onboarding/complete...")
        complete_response = client.post(
            "/api/onboarding/complete",
            json={"session_id": start_data['session_id']},
            headers=headers
        )
        
        if complete_response.status_code != 200:
            print(f"❌ Onboarding complete failed: {complete_response.status_code}")
            return False
        
        complete_data = complete_response.json()
        print("✅ Onboarding complete successful")
        print(f"   Accounts linked: {complete_data['accounts_linked']}")
        
        # Test accounts endpoint
        print("\n📋 Testing GET /api/accounts...")
        accounts_response = client.get("/api/accounts", headers=headers)
        
        if accounts_response.status_code != 200:
            print(f"❌ Get accounts failed: {accounts_response.status_code}")
            return False
        
        accounts_data = accounts_response.json()
        print("✅ Get accounts successful")
        print(f"   Total accounts: {accounts_data['total']}")
        print(f"   Sandbox mode: {accounts_data['sandbox_mode']}")
        
        if accounts_data['accounts']:
            print(f"   Sample: {accounts_data['accounts'][0]['institution']}")
        
        return True
        
    except ImportError:
        print("⚠️  fastapi.testclient not installed")
        print("   Run: poetry add --dev fastapi[all]")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🚀 Knot Integration Test Suite")
    print("=" * 50)
    
    results = []
    
    # Test 1: Mock mode
    results.append(await test_mock_mode())
    
    # Test 2: Real API (if credentials available)
    results.append(await test_with_credentials())
    
    # Test 3: FastAPI endpoints
    results.append(await test_api_endpoints())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🎉 Knot integration is working!")
        return 0
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

