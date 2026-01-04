#!/usr/bin/env python3
"""
Quick test for the wallet endpoint specifically
"""

import requests
import json

def test_wallet_endpoint():
    """Test the wallet endpoint that was causing CORS issues"""
    
    print("=" * 60)
    print("Testing Wallet Endpoint")
    print("=" * 60)
    
    # Test the exact endpoint that was failing
    wallet_address = "0x385bc87f1496c61e067e83d005711f5db06f2d45"
    url = f"http://localhost:8000/api/users/wallet/{wallet_address}"
    
    headers = {
        "Origin": "http://localhost:3002",
        "Content-Type": "application/json"
    }
    
    print(f"Testing: {url}")
    print(f"Headers: {headers}")
    print()
    
    try:
        # Test with a shorter timeout
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✓ SUCCESS: User found")
            print(f"Response: {response.json()}")
        elif response.status_code == 404:
            print("✓ SUCCESS: User not found (expected for new wallet)")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ UNEXPECTED STATUS: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Check CORS headers
        cors_origin = response.headers.get('access-control-allow-origin')
        if cors_origin:
            print(f"✓ CORS Origin: {cors_origin}")
        else:
            print("✗ Missing CORS headers")
            
    except requests.exceptions.Timeout:
        print("✗ TIMEOUT: Request took too long")
        print("This might indicate MongoDB connection issues")
    except requests.exceptions.ConnectionError:
        print("✗ CONNECTION ERROR: Server not running?")
    except Exception as e:
        print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    test_wallet_endpoint()