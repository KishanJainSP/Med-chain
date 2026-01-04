"""
Quick CORS fix verification
"""
import subprocess
import time
import requests
import sys

def check_server_running():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_cors_quickly():
    """Quick CORS test"""
    try:
        # Test OPTIONS request
        response = requests.options(
            "http://localhost:8000/api/health",
            headers={
                "Origin": "http://localhost:3002",
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            return False, f"OPTIONS failed: {response.status_code}"
        
        # Test GET request
        response = requests.get(
            "http://localhost:8000/api/health",
            headers={"Origin": "http://localhost:3002"},
            timeout=5
        )
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        
        if not cors_header:
            return False, "No CORS header in response"
        
        if cors_header != "http://localhost:3002":
            return False, f"Wrong CORS header: {cors_header}"
        
        return True, "CORS working correctly"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 60)
    print("CORS Quick Fix Verification")
    print("=" * 60)
    
    # Check if server is running
    print("\n[1] Checking if server is running...")
    if check_server_running():
        print("✓ Server is running")
    else:
        print("✗ Server is not running")
        print("\nPlease start the server:")
        print("  cd backend")
        print("  python start_server.py")
        print("\nThen run this script again.")
        return False
    
    # Test CORS
    print("\n[2] Testing CORS...")
    success, message = test_cors_quickly()
    
    if success:
        print(f"✓ {message}")
        print("\n" + "=" * 60)
        print("✓ CORS IS WORKING!")
        print("=" * 60)
        print("\nYour frontend should now work.")
        print("\nNext steps:")
        print("  1. Refresh your frontend (Ctrl+Shift+R)")
        print("  2. Try the login again")
        print("  3. Check browser console - should be no CORS errors")
        return True
    else:
        print(f"✗ {message}")
        print("\n" + "=" * 60)
        print("✗ CORS STILL NOT WORKING")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Restart the server:")
        print("     - Stop current server (Ctrl+C)")
        print("     - python backend/start_server.py")
        print("  2. Run full test: python backend/test_user_endpoint.py")
        print("  3. Check server logs for CORS messages")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)