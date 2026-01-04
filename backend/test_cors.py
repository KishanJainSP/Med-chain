"""
Test CORS configuration
"""
import requests

def test_cors():
    """Test CORS with OPTIONS request"""
    print("=" * 60)
    print("Testing CORS Configuration")
    print("=" * 60)
    
    # Test OPTIONS request (preflight)
    print("\n[1] Testing OPTIONS request (CORS preflight)...")
    try:
        response = requests.options(
            "http://localhost:8000/api/health",
            headers={
                "Origin": "http://localhost:3002",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Headers:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"    {header}: {value}")
        
        if response.status_code == 200:
            print("\n✓ OPTIONS request successful")
        else:
            print(f"\n✗ OPTIONS request failed: {response.status_code}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nIs the server running?")
        print("  Run: python backend/start_server.py")
        return False
    
    # Test actual GET request
    print("\n[2] Testing GET request with Origin header...")
    try:
        response = requests.get(
            "http://localhost:8000/api/health",
            headers={"Origin": "http://localhost:3002"}
        )
        
        print(f"  Status: {response.status_code}")
        
        # Check CORS headers
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        print(f"  Access-Control-Allow-Origin: {cors_header}")
        
        if cors_header:
            print("\n✓ CORS headers present")
            return True
        else:
            print("\n✗ CORS headers missing")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    # Test the problematic endpoint
    print("\n[3] Testing /api/users/wallet endpoint...")
    try:
        response = requests.get(
            "http://localhost:8000/api/users/wallet/0x385bc87f1496c61e067e83d005711f5db06f2d45",
            headers={"Origin": "http://localhost:3002"}
        )
        
        print(f"  Status: {response.status_code}")
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        print(f"  Access-Control-Allow-Origin: {cors_header}")
        
        if cors_header:
            print("\n✓ CORS working on wallet endpoint")
            return True
        else:
            print("\n✗ CORS not working on wallet endpoint")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("MedChain CORS Test")
    print("=" * 60)
    
    success = test_cors()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ CORS is configured correctly!")
        print("=" * 60)
        print("\nYour frontend should now be able to connect.")
    else:
        print("\n" + "=" * 60)
        print("✗ CORS issues detected")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Restart the server: python backend/start_server.py")
        print("  2. Check server logs for CORS messages")
        print("  3. Verify frontend is on http://localhost:3002")

if __name__ == "__main__":
    main()
