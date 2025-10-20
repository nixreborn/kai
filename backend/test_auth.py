"""Simple script to test authentication endpoints without starting the full server."""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import only the auth router, avoiding the agents module
import importlib.util
spec = importlib.util.spec_from_file_location("auth_module", backend_dir / "src" / "api" / "auth.py")
auth_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth_module)

from src.models.database import Base
from src.models.db_session import engine

app = FastAPI()
app.include_router(auth_module.router)

async def init_test_db():
    """Initialize test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

client = TestClient(app)

print("=" * 80)
print("Testing Kai Authentication System")
print("=" * 80)

# Test 1: Register a new user
print("\n1. Testing User Registration...")
register_response = client.post(
    "/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "testpassword123"
    }
)
print(f"   Status Code: {register_response.status_code}")
print(f"   Response: {register_response.json()}")

if register_response.status_code == 201:
    print("   ✓ User registration successful!")
else:
    print("   ✗ User registration failed!")

# Test 2: Login with the user
print("\n2. Testing User Login...")
login_response = client.post(
    "/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "testpassword123"
    }
)
print(f"   Status Code: {login_response.status_code}")
print(f"   Response: {login_response.json()}")

if login_response.status_code == 200:
    print("   ✓ User login successful!")
    token_data = login_response.json()
    access_token = token_data["access_token"]
else:
    print("   ✗ User login failed!")
    access_token = None

# Test 3: Get current user info
if access_token:
    print("\n3. Testing Get Current User Info...")
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"   Status Code: {me_response.status_code}")
    print(f"   Response: {me_response.json()}")

    if me_response.status_code == 200:
        print("   ✓ Get current user info successful!")
    else:
        print("   ✗ Get current user info failed!")

    # Test 4: Refresh token
    print("\n4. Testing Token Refresh...")
    refresh_response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"   Status Code: {refresh_response.status_code}")
    print(f"   Response: {refresh_response.json()}")

    if refresh_response.status_code == 200:
        print("   ✓ Token refresh successful!")
    else:
        print("   ✗ Token refresh failed!")

    # Test 5: Logout
    print("\n5. Testing User Logout...")
    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"   Status Code: {logout_response.status_code}")
    print(f"   Response: {logout_response.json()}")

    if logout_response.status_code == 200:
        print("   ✓ User logout successful!")
    else:
        print("   ✗ User logout failed!")

# Test 6: Try to login with wrong password
print("\n6. Testing Login with Wrong Password...")
wrong_password_response = client.post(
    "/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "wrongpassword"
    }
)
print(f"   Status Code: {wrong_password_response.status_code}")
print(f"   Response: {wrong_password_response.json()}")

if wrong_password_response.status_code == 401:
    print("   ✓ Wrong password correctly rejected!")
else:
    print("   ✗ Wrong password not properly handled!")

# Test 7: Try to register duplicate email
print("\n7. Testing Duplicate Email Registration...")
duplicate_response = client.post(
    "/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "anotherpassword123"
    }
)
print(f"   Status Code: {duplicate_response.status_code}")
print(f"   Response: {duplicate_response.json()}")

if duplicate_response.status_code == 400:
    print("   ✓ Duplicate email correctly rejected!")
else:
    print("   ✗ Duplicate email not properly handled!")

print("\n" + "=" * 80)
print("Authentication System Test Complete!")
print("=" * 80)
