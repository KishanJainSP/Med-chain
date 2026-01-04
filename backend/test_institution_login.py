#!/usr/bin/env python3
"""
Test institution login to debug the user check issue
"""

import requests
import json

def test_institution_login():
    """Test the institution login flow"""
    
    print("=" * 60)
    print("Testing Institution Login Flow")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Test wallet address (you can replace with the actual one you're using)
    test_wallet = "0x1234567890abcdef1234567890abcdef12345678"
    
    # Step 1: Test user lookup endpoint directly
    print("1. Testing user lookup endpoint...")
    try:
        response = requests.get(f"{base_url}/users/wallet/{test_wallet}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("✓ 404 is expected for unregistered wallet")
        elif response.status_code == 200:
            print("✓ User found in database")
            user_data = response.json()
            print(f"User type: {user_data.get('user_type')}")
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing user lookup: {e}")
        return False
    
    # Step 2: Create a test institution
    print("\n2. Creating test institution...")
    try:
        institution_data = {
            "name": "Test Medical Center",
            "wallet_address": test_wallet,
            "license_number": "LIC123456",
            "address": "123 Medical St, Health City",
            "phone": "555-0123",
            "email": "admin@testmedical.com"
        }
        
        response = requests.post(f"{base_url}/institutions", json=institution_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Institution created successfully")
        elif response.status_code == 409:
            print("✓ Institution already exists (expected)")
        else:
            print(f"✗ Failed to create institution: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error creating institution: {e}")
    
    # Step 3: Test user lookup again after creating institution
    print("\n3. Testing user lookup after institution creation...")
    try:
        response = requests.get(f"{base_url}/users/wallet/{test_wallet}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✓ Institution found successfully")
            print(f"User type: {user_data.get('user_type')}")
            print(f"Name: {user_data.get('name')}")
            print(f"Email: {user_data.get('email')}")
        else:
            print(f"✗ Institution not found after creation: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error in second lookup: {e}")
    
    # Step 4: Test with different wallet formats
    print("\n4. Testing wallet address formats...")
    
    # Test with uppercase
    test_wallet_upper = test_wallet.upper()
    try:
        response = requests.get(f"{base_url}/users/wallet/{test_wallet_upper}")
        print(f"Uppercase wallet: {response.status_code}")
    except Exception as e:
        print(f"Uppercase wallet error: {e}")
    
    # Test with mixed case
    test_wallet_mixed = "0x1234ABCD5678efgh9012IJKL3456mnop78901234"
    try:
        response = requests.get(f"{base_url}/users/wallet/{test_wallet_mixed}")
        print(f"Mixed case wallet: {response.status_code}")
    except Exception as e:
        print(f"Mixed case wallet error: {e}")
    
    return True

def check_server_health():
    """Check if server is healthy"""
    
    print("\n" + "=" * 60)
    print("Checking Server Health")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/api/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print("✓ Server is healthy")
            print(f"Status: {health_data.get('status')}")
            print(f"AI Models: {health_data.get('ai_models', {})}")
        else:
            print(f"✗ Server health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Cannot reach server: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Institution Login Issue")
    
    # Check server health first
    check_server_health()
    
    # Test institution login flow
    success = test_institution_login()
    
    print("\n" + "=" * 60)
    print("DEBUGGING SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ Basic endpoints are working")
        print("\nIf you're still getting login errors, please:")
        print("1. Check the exact wallet address you're using")
        print("2. Ensure the wallet address format is correct")
        print("3. Check browser console for detailed error messages")
        print("4. Try refreshing the page (Ctrl+Shift+R)")
    else:
        print("❌ Found issues with the endpoints")
        print("Check server logs for detailed error messages")
    
    print("=" * 60)