#!/usr/bin/env python3
"""
Test script for password recovery API endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/auth"

def test_password_reset_request():
    """Test password reset request endpoint"""
    print("🧪 Testing Password Reset Request...")
    
    url = f"{BASE_URL}/password-reset-request/"
    data = {"email": "test@example.com"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset request successful")
            return True
        else:
            print("❌ Password reset request failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_token_validation():
    """Test token validation endpoint"""
    print("\n🧪 Testing Token Validation...")
    
    url = f"{BASE_URL}/password-reset-validate/"
    data = {"token": "invalid-token", "uid": "123"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:  # Expected for invalid token
            print("✅ Token validation correctly rejected invalid token")
            return True
        else:
            print("❌ Token validation unexpected response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_password_reset_confirm():
    """Test password reset confirmation endpoint"""
    print("\n🧪 Testing Password Reset Confirmation...")
    
    url = f"{BASE_URL}/password-reset-confirm/"
    data = {
        "token": "invalid-token",
        "uid": "123",
        "password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:  # Expected for invalid token
            print("✅ Password reset confirmation correctly rejected invalid token")
            return True
        else:
            print("❌ Password reset confirmation unexpected response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_legacy_endpoints():
    """Test legacy endpoints for backward compatibility"""
    print("\n🧪 Testing Legacy Endpoints...")
    
    # Test legacy forgot password
    url = f"{BASE_URL}/forgot-password/"
    data = {"email": "test@example.com"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Legacy Forgot Password - Status: {response.status_code}")
        
        if response.status_code in [200, 404]:  # 404 expected if no user exists
            print("✅ Legacy forgot password endpoint working")
            return True
        else:
            print("❌ Legacy forgot password endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Password Recovery API Tests")
    print("=" * 50)
    
    tests = [
        test_password_reset_request,
        test_token_validation,
        test_password_reset_confirm,
        test_legacy_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Password recovery API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
