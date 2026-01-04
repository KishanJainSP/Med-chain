"""
Test user endpoint and CORS
"""
import sys
import requests
import json

def test_cors_preflight():
    """Test CORS preflight request"""
    print("=" * 60)
    print("Testing CORS Preflight (OPTIONS)")
    print("=" * 60)
    
    try:
        response = requests.options(
            "http://localhost:8000/api/users/wallet/test",
            headers={
                "Origin": "http://localhost:3002",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=5
        )
        
        print(f"\nStatus: {response.status_code}")
        
        # Check CORS headers
        cors_headers = {}
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                cors_headers[header] = value
                print(f"  {header}: {value}")
        
        if response.status_code == 200 and cors_headers:
            print("\n✓ CORS preflight successful")
            return True
        else:
            print(f"\n✗ CORS preflight failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nIs the server running? Run: python backend/start_server.py")
        return False

def test_user_endpoint():
    """Test the actual user endpoint"""
    print("\n" + "=" * 60)
    print("Testing User Endpoint")
    print("=" * 60)
    
    wallet = "0x385bc87f1496c61e067e83d005711f5db06f2d45"
    url = f"http://localhost:8000/api/users/wallet/{wallet}"
    
    print(f"\nTesting: {url}")
    print("With Origin: http://localhost:3002")
    
    try:
        response = requests.get(
            url,
            headers={
                "Origin": "http://localhost:3002",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"\nStatus: {response.status_code}")
        
        # Check CORS headers in response
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        print(f"Access-Control-Allow-Origin: {cors_origin}")
        
        # Check response content
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if cors_origin:
            print("\n✓ CORS headers present in response")
            if response.status_code == 404:
                print("✓ Endpoint working (404 = user not found, which is expected)")
                return True
            elif response.status_code == 200:
                print("✓ Endpoint working (200 = user found)")
                return True
            else:
                print(f"⚠ Unexpected status code: {response.status_code}")
                return False
        else:
            print("\n✗ No CORS headers in response")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint for comparison"""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint (for comparison)")
    print("=" * 60)
    
    try:
        response = requests.get(
            "http://localhost:8000/api/health",
            headers={"Origin": "http://localhost:3002"},
            timeout=5
        )
        
        print(f"\nStatus: {response.status_code}")
        
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        print(f"Access-Control-Allow-Origin: {cors_origin}")
        
        if cors_origin and response.status_code == 200:
            print("\n✓ Health endpoint working with CORS")
            return True
        else:
            print("\n✗ Health endpoint has issues")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def create_test_user():
    """Create a test user to verify the endpoint works"""
    print("\n" + "=" * 60)
    print("Creating Test User")
    print("=" * 60)
    
    test_patient = {
        "name": "Test Patient",
        "wallet_address": "0x385bc87f1496c61e067e83d005711f5db06f2d45",
        "date_of_birth": "1990-01-01",
        "gender": "Male",
        "blood_group": "O+",
        "phone": "+1234567890",
        "email": "test@example.com",
        "emergency_contact": "+1234567891"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/patients",
            json=test_patient,
            headers={"Origin": "http://localhost:3002"},
            timeout=10
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Test user created: {data}")
            return True
        elif response.status_code == 409:
            print("✓ Test user already exists")
            return True
        else:
            print(f"⚠ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error creating test user: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("MedChain User Endpoint & CORS Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: CORS preflight
    results.append(("CORS Preflight", test_cors_preflight()))
    
    # Test 2: Health endpoint (baseline)
    results.append(("Health Endpoint", test_health_endpoint()))
    
    # Test 3: Create test user
    results.append(("Create Test User", create_test_user()))
    
    # Test 4: User endpoint
    results.append(("User Endpoint", test_user_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        print("\nYour frontend should now work without CORS errors.")
        print("\nNext steps:")
        print("  1. Restart your frontend")
        print("  2. Hard refresh (Ctrl+Shift+R)")
        print("  3. Try logging in")
    else:
        print("\n✗ Some tests failed.")
        print("\nTroubleshooting:")
        print("  1. Restart server: python backend/start_server.py")
        print("  2. Check MongoDB is running")
        print("  3. Check server logs for errors")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)