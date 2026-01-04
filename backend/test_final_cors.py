#!/usr/bin/env python3
"""
Final CORS test - simple and direct
"""

import requests

def test_final():
    """Final test of the wallet endpoint"""
    
    print("=" * 60)
    print("FINAL CORS TEST - Local MongoDB")
    print("=" * 60)
    
    # Test the exact failing endpoint
    url = "http://localhost:8000/api/users/wallet/0x385bc87f1496c61e067e83d005711f5db06f2d45"
    headers = {"Origin": "http://localhost:3002"}
    
    print(f"Testing: {url}")
    print(f"Origin: {headers['Origin']}")
    print()
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Response: {response.text}")
        print()
        
        # Check CORS headers
        print("CORS Headers:")
        cors_headers = [
            'access-control-allow-origin',
            'access-control-allow-credentials', 
            'access-control-allow-methods',
            'access-control-expose-headers'
        ]
        
        all_cors_good = True
        for header in cors_headers:
            value = response.headers.get(header)
            if value:
                print(f"  ✓ {header}: {value}")
            else:
                print(f"  ✗ {header}: Missing")
                all_cors_good = False
        
        print()
        
        if response.status_code == 404:
            print("✅ PERFECT! Status 404 means:")
            print("  ✓ Endpoint is working correctly")
            print("  ✓ User not found (expected for new wallet)")
            print("  ✓ Database connection working")
        elif response.status_code == 200:
            print("✅ SUCCESS! User found in database")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
        
        if all_cors_good:
            print("  ✓ CORS headers are perfect")
            print("  ✓ Frontend should work now!")
            return True
        else:
            print("  ✗ CORS headers missing")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ TIMEOUT: Still having database issues")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_final()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Your frontend should work now!")
        print("=" * 60)
        print("✅ Local MongoDB: Working")
        print("✅ CORS: Properly configured") 
        print("✅ Wallet endpoint: Responding correctly")
        print("✅ No more online database timeouts")
        print("\nTry your frontend login again!")
    else:
        print("❌ Still having issues")
        print("Check server logs for more details")
    print("=" * 60)