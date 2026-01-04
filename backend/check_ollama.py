"""
Check Ollama installation and status on Windows
Works even if Ollama is not in PATH
"""
import requests
import subprocess
import os
import sys

def check_ollama_service():
    """Check if Ollama service is running"""
    print("=" * 60)
    print("Checking Ollama Installation")
    print("=" * 60)
    
    # Check if Ollama service is responding
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("\n✓ Ollama service is running!")
            print(f"  URL: http://localhost:11434")
            
            # List available models
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print(f"\n✓ Found {len(models)} installed model(s):")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) / (1024**3)  # Convert to GB
                    print(f"  - {name} ({size:.2f} GB)")
                return True, models
            else:
                print("\n⚠ Ollama is running but no models are installed")
                print("\nTo install the recommended model, run:")
                print("  python backend/install_ollama_model.py")
                return True, []
        else:
            print(f"\n✗ Ollama service returned status code: {response.status_code}")
            return False, []
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to Ollama service")
        print("\nOllama might not be running. Please:")
        print("  1. Open Ollama from Start menu")
        print("  2. Or search for 'Ollama' in Windows search")
        print("  3. Wait a few seconds for it to start")
        return False, []
    except Exception as e:
        print(f"\n✗ Error checking Ollama: {e}")
        return False, []

def check_ollama_executable():
    """Find Ollama executable location"""
    print("\n" + "=" * 60)
    print("Checking Ollama Executable")
    print("=" * 60)
    
    # Common installation paths
    possible_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Ollama\ollama.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"\n✓ Found Ollama executable:")
            print(f"  {path}")
            return path
    
    print("\n⚠ Could not find Ollama executable in common locations")
    print("\nIf Ollama is installed, you can still use it via the API")
    return None

def test_ollama_api():
    """Test Ollama API with a simple query"""
    print("\n" + "=" * 60)
    print("Testing Ollama API")
    print("=" * 60)
    
    try:
        # Check if any model is available
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("\n✗ Ollama API not responding")
            return False
        
        models = response.json().get("models", [])
        if not models:
            print("\n⚠ No models installed. Cannot test API.")
            print("\nInstall a model first:")
            print("  python backend/install_ollama_model.py")
            return False
        
        # Use first available model
        model_name = models[0].get("name", "").split(":")[0]
        print(f"\nTesting with model: {model_name}")
        print("Sending test query: 'What is 2+2?'")
        
        test_payload = {
            "model": model_name,
            "prompt": "What is 2+2? Answer in one short sentence.",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            print(f"\n✓ Ollama API is working!")
            print(f"  Response: {answer[:100]}...")
            return True
        else:
            print(f"\n✗ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing API: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("MedChain Ollama Diagnostic Tool")
    print("=" * 60)
    
    # Step 1: Check service
    service_running, models = check_ollama_service()
    
    # Step 2: Check executable
    exe_path = check_ollama_executable()
    
    # Step 3: Test API if service is running and models exist
    if service_running and models:
        api_working = test_ollama_api()
    else:
        api_working = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if service_running and models and api_working:
        print("\n✓ SUCCESS! Ollama is fully functional")
        print("\nYou can now:")
        print("  1. Run: python backend/test_ollama.py")
        print("  2. Start server: python backend/start_server.py")
        print("  3. Use MedChain with Ollama-enhanced AI!")
        return True
    elif service_running and not models:
        print("\n⚠ Ollama is running but needs a model")
        print("\nNext step:")
        print("  Run: python backend/install_ollama_model.py")
        return False
    elif not service_running:
        print("\n✗ Ollama service is not running")
        print("\nNext steps:")
        print("  1. Open Ollama from Windows Start menu")
        print("  2. Wait 10 seconds for it to start")
        print("  3. Run this script again: python backend/check_ollama.py")
        return False
    else:
        print("\n⚠ Ollama is partially working")
        print("\nTry:")
        print("  1. Restart Ollama from Start menu")
        print("  2. Run: python backend/install_ollama_model.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
