#!/usr/bin/env python3
"""
Test CORS with fresh local setup
"""

import requests
import time

def test_fresh_cors():
    """Test CORS with the fresh server setup"""
    
    print("=" * 50)
    print("Testing Fresh Server CORS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    headers = {"Origin": "http://localhost:3002"}
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server is running")
                break
        except:
            time.sleep(1)
            print(f"  Waiting... ({i+1}/10)")
    else:
        print("✗ Server not responding")
        return False
    
    # Test CORS
    try:
        print("\nTesting CORS...")
        response = requests.get(f"{base_url}/api/health", headers=headers, timeout=3)
        
        print(f"Status: {response.status_code}")
        
        cors_origin = response.headers.get('access-control-allow-origin')
        if cors_origin == "http://localhost:3002":
            print("✓ CORS working perfectly!")
        else:
            print(f"✗ CORS issue: {cors_origin}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test wallet endpoint
    try:
        print("\nTesting wallet endpoint...")
        wallet = "0x385bc87f1496c61e067e83d005711f5db06f2d45"
        response = requests.get(
            f"{base_url}/api/users/wallet/{wallet}", 
            headers=headers, 
            timeout=5
        )
        
        print(f"Wallet endpoint status: {response.status_code}")
        
        if response.status_code == 404:
            print("✓ Perfect! 404 means endpoint works (user not registered)")
        elif response.status_code == 200:
            print("✓ User found in database")
        else:
            print(f"Response: {response.text}")
            
        # Check CORS headers
        cors_origin = response.headers.get('access-control-allow-origin')
        if cors_origin == "http://localhost:3002":
            print("✓ Wallet endpoint CORS working!")
            return True
        else:
            print(f"✗ Wallet endpoint CORS issue: {cors_origin}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Wallet endpoint timeout - database issue")
        return False
    except Exception as e:
        print(f"✗ Wallet endpoint error: {e}")
        return False

if __name__ == "__main__":
    success = test_fresh_cors()
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your frontend should work now!")
    else:
        print("\n❌ Some tests failed")
        print("Check server logs for issues")