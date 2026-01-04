#!/usr/bin/env python3
"""
Test the exact endpoint that was failing in the frontend
"""

import requests
import json

def test_simple():
    """Test with the exact wallet address from the error"""
    
    print("=" * 60)
    print("Testing Exact Frontend Request")
    print("=" * 60)
    
    # This is the exact request that was failing
    wallet = "0x385bc87f1496c61e067e83d005711f5db06f2d45"
    url = f"http://localhost:8000/api/users/wallet/{wallet}"
    
    headers = {
        "Origin": "http://localhost:3002"
    }
    
    print(f"URL: {url}")
    print(f"Origin: {headers['Origin']}")
    print()
    
    try:
        # Use a very short timeout to avoid hanging
        response = requests.get(url, headers=headers, timeout=2)
        
        print(f"✓ Status: {response.status_code}")
        
        # Check CORS headers first
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-credentials': response.headers.get('access-control-allow-credentials'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods')
        }
        
        print("CORS Headers:")
        for key, value in cors_headers.items():
            if value:
                print(f"  ✓ {key}: {value}")
            else:
                print(f"  ✗ {key}: Missing")
        
        print()
        
        if response.status_code == 404:
            print("✓ PERFECT: 404 Not Found (expected for unregistered wallet)")
            print("✓ This means the endpoint is working correctly")
            print("✓ CORS is working")
            print("✓ Frontend should be able to handle this response")
        elif response.status_code == 200:
            print("✓ SUCCESS: User found")
            print(f"Data: {response.json()}")
        else:
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ TIMEOUT: Database query is taking too long")
        print("Recommendation: Check MongoDB performance or add database indexes")
    except Exception as e:
        print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    test_simple()