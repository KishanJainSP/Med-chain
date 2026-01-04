#!/usr/bin/env python3
"""
Test the specific wallet address from the logs
"""

import requests
import json

def test_specific_wallet():
    """Test the wallet address that was in the server logs"""
    
    print("=" * 60)
    print("Testing Specific Wallet Address")
    print("=" * 60)
    
    # This is the wallet address from the server logs
    wallet_address = "0x97d2dc5813705bdcb3a1b6757060dd3b184ccde5"
    
    base_url = "http://localhost:8000/api"
    
    print(f"Testing wallet: {wallet_address}")
    
    try:
        response = requests.get(f"{base_url}/users/wallet/{wallet_address}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("\n✅ SUCCESS! User found:")
            print(f"  User Type: {user_data.get('user_type')}")
            print(f"  User ID: {user_data.get('user_id')}")
            print(f"  Name: {user_data.get('name')}")
            print(f"  Email: {user_data.get('email')}")
            print(f"  Wallet: {user_data.get('wallet_address')}")
            
            print("\n📋 Frontend should receive this exact structure:")
            print(json.dumps(user_data, indent=2))
            
        elif response.status_code == 404:
            print("❌ User not found (404)")
            print("This wallet needs to be registered first")
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_wallet()