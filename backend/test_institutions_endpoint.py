#!/usr/bin/env python3
"""
Test the institutions endpoint to see why the list is not showing
"""

import requests
import json

def test_institutions_endpoint():
    """Test the institutions list endpoint"""
    
    print("=" * 60)
    print("Testing Institutions Endpoint")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Get all institutions
    print("1. Testing GET /institutions endpoint...")
    try:
        response = requests.get(f"{base_url}/institutions")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            institutions = response.json()
            print(f"\n✅ SUCCESS! Found {len(institutions)} institutions:")
            
            if len(institutions) == 0:
                print("⚠️  No institutions in database")
                print("This is why the dropdown is empty!")
            else:
                for i, inst in enumerate(institutions):
                    print(f"  {i+1}. {inst.get('name', 'No name')} (ID: {inst.get('id', 'No ID')[:8]}...)")
                    print(f"     Email: {inst.get('email', 'No email')}")
                    print(f"     Wallet: {inst.get('wallet_address', 'No wallet')}")
        else:
            print(f"❌ Failed to get institutions: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing institutions endpoint: {e}")
        return False
    
    # Test 2: Check if we have any institutions in the database
    print(f"\n2. Checking database for institutions...")
    
    # Let's create a test institution if none exist
    if response.status_code == 200:
        institutions = response.json()
        if len(institutions) == 0:
            print("Creating test institutions for doctor registration...")
            
            test_institutions = [
                {
                    "name": "City General Hospital",
                    "wallet_address": "0x1111111111111111111111111111111111111111",
                    "license_number": "HOSP001",
                    "address": "123 Medical Center Dr, Health City",
                    "phone": "555-0001",
                    "email": "admin@citygeneral.com"
                },
                {
                    "name": "Regional Medical Center", 
                    "wallet_address": "0x2222222222222222222222222222222222222222",
                    "license_number": "HOSP002",
                    "address": "456 Healthcare Ave, Medical Town",
                    "phone": "555-0002",
                    "email": "contact@regionalmed.com"
                },
                {
                    "name": "University Hospital",
                    "wallet_address": "0x3333333333333333333333333333333333333333", 
                    "license_number": "HOSP003",
                    "address": "789 University Blvd, Campus City",
                    "phone": "555-0003",
                    "email": "info@univhospital.edu"
                }
            ]
            
            created_count = 0
            for inst_data in test_institutions:
                try:
                    create_response = requests.post(f"{base_url}/institutions", json=inst_data)
                    if create_response.status_code == 200:
                        created_count += 1
                        print(f"✓ Created: {inst_data['name']}")
                    elif create_response.status_code == 409:
                        print(f"✓ Already exists: {inst_data['name']}")
                    else:
                        print(f"✗ Failed to create {inst_data['name']}: {create_response.status_code}")
                except Exception as e:
                    print(f"✗ Error creating {inst_data['name']}: {e}")
            
            print(f"\nCreated {created_count} new institutions")
            
            # Test the endpoint again
            print("\n3. Testing institutions endpoint after creating test data...")
            try:
                response = requests.get(f"{base_url}/institutions")
                if response.status_code == 200:
                    institutions = response.json()
                    print(f"✅ Now found {len(institutions)} institutions:")
                    for i, inst in enumerate(institutions):
                        print(f"  {i+1}. {inst.get('name', 'No name')}")
                else:
                    print(f"❌ Still failing: {response.status_code}")
            except Exception as e:
                print(f"❌ Error in second test: {e}")
    
    return True

def test_cors_for_institutions():
    """Test CORS for institutions endpoint"""
    
    print("\n" + "=" * 60)
    print("Testing CORS for Institutions Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(
            "http://localhost:8000/api/institutions",
            headers={"Origin": "http://localhost:3002"}
        )
        
        print(f"Status: {response.status_code}")
        cors_origin = response.headers.get('access-control-allow-origin')
        if cors_origin:
            print(f"✅ CORS Origin: {cors_origin}")
        else:
            print("❌ No CORS headers found")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")

if __name__ == "__main__":
    print("🏥 Testing Institutions Endpoint for Doctor Registration")
    
    success = test_institutions_endpoint()
    test_cors_for_institutions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Institutions endpoint testing complete!")
        print("\nIf institutions list still not showing in frontend:")
        print("1. Check browser console for JavaScript errors")
        print("2. Verify the frontend is calling the correct API endpoint")
        print("3. Check network tab to see if the request is being made")
        print("4. Hard refresh the page (Ctrl+Shift+R)")
    else:
        print("❌ Found issues with institutions endpoint")
    print("=" * 60)