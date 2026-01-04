#!/usr/bin/env python3
"""
Test CORS without database operations
"""

import requests

def test_cors_only():
    """Test CORS on endpoints that don't require database"""
    
    print("=" * 60)
    print("Testing CORS (No Database)")
    print("=" * 60)
    
    headers = {"Origin": "http://localhost:3002"}
    
    # Test health endpoint (no database required)
    try:
        response = requests.get("http://localhost:8000/api/health", headers=headers, timeout=3)
        print(f"Health endpoint: {response.status_code}")
        
        cors_origin = response.headers.get('access-control-allow-origin')
        if cors_origin == "http://localhost:3002":
            print("✓ CORS is working perfectly!")
        else:
            print(f"✗ CORS issue: {cors_origin}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test OPTIONS request (CORS preflight)
    try:
        response = requests.options(
            "http://localhost:8000/api/users/wallet/test", 
            headers={
                "Origin": "http://localhost:3002",
                "Access-Control-Request-Method": "GET"
            }, 
            timeout=3
        )
        print(f"OPTIONS request: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ CORS preflight working!")
        else:
            print("✗ CORS preflight failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_cors_only()