"""
Install Ollama model using API (works without ollama command in PATH)
"""
import requests
import time
import sys

OLLAMA_API = "http://localhost:11434"
RECOMMENDED_MODEL = "llama3.2"

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def list_installed_models():
    """List currently installed models"""
    try:
        response = requests.get(f"{OLLAMA_API}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name", "") for m in models]
        return []
    except:
        return []

def pull_model(model_name):
    """Pull a model using Ollama API"""
    print(f"\nPulling model: {model_name}")
    print("This may take several minutes depending on your internet connection...")
    print("Model size: ~2GB for llama3.2")
    print("\nProgress:")
    
    try:
        # Use streaming to show progress
        response = requests.post(
            f"{OLLAMA_API}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=600  # 10 minutes timeout
        )
        
        if response.status_code == 200:
            last_status = ""
            for line in response.iter_lines():
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        status = data.get("status", "")
                        
                        # Show progress
                        if status != last_status:
                            if "pulling" in status.lower():
                                print(f"  {status}")
                            elif "downloading" in status.lower():
                                total = data.get("total", 0)
                                completed = data.get("completed", 0)
                                if total > 0:
                                    percent = (completed / total) * 100
                                    print(f"  Downloading: {percent:.1f}%", end="\r")
                            elif "verifying" in status.lower():
                                print(f"\n  {status}")
                            elif "success" in status.lower():
                                print(f"\n  {status}")
                            last_status = status
                    except:
                        pass
            
            print(f"\n✓ Successfully pulled model: {model_name}")
            return True
        else:
            print(f"\n✗ Failed to pull model. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out. Please check your internet connection.")
        return False
    except Exception as e:
        print(f"\n✗ Error pulling model: {e}")
        return False

def main():
    print("=" * 60)
    print("Ollama Model Installation")
    print("=" * 60)
    
    # Check if Ollama is running
    print("\n[Step 1] Checking Ollama service...")
    if not check_ollama_running():
        print("✗ Ollama is not running!")
        print("\nPlease:")
        print("  1. Open Ollama from Windows Start menu")
        print("  2. Wait 10 seconds for it to start")
        print("  3. Run this script again")
        return False
    
    print("✓ Ollama is running")
    
    # Check installed models
    print("\n[Step 2] Checking installed models...")
    installed = list_installed_models()
    
    if installed:
        print(f"✓ Found {len(installed)} installed model(s):")
        for model in installed:
            print(f"  - {model}")
        
        # Check if recommended model is already installed
        if any(RECOMMENDED_MODEL in m for m in installed):
            print(f"\n✓ Recommended model '{RECOMMENDED_MODEL}' is already installed!")
            print("\nYou're ready to use Ollama with MedChain!")
            print("Run: python backend/test_ollama.py")
            return True
    else:
        print("⚠ No models installed yet")
    
    # Ask user to install
    print(f"\n[Step 3] Installing recommended model: {RECOMMENDED_MODEL}")
    print("\nRecommended models:")
    print("  1. llama3.2 (2GB) - Recommended, balanced performance")
    print("  2. llama3.2:1b (1.3GB) - Smaller, faster")
    print("  3. llama3.1 (4.7GB) - Larger, more capable")
    
    print(f"\nInstalling: {RECOMMENDED_MODEL}")
    choice = input("Continue? (Y/n): ").strip().lower()
    
    if choice and choice != 'y':
        print("\nInstallation cancelled.")
        print("\nTo install manually, you can:")
        print("  1. Open Ollama from Start menu")
        print("  2. It will open a terminal")
        print(f"  3. Type: ollama pull {RECOMMENDED_MODEL}")
        return False
    
    # Pull the model
    success = pull_model(RECOMMENDED_MODEL)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ SUCCESS! Model installed successfully")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Test integration: python backend/test_ollama.py")
        print("  2. Start server: python backend/start_server.py")
        print("  3. Use MedChain with Ollama-enhanced AI!")
        return True
    else:
        print("\n" + "=" * 60)
        print("✗ Installation failed")
        print("=" * 60)
        print("\nAlternative method:")
        print("  1. Open Ollama from Start menu")
        print("  2. A terminal window will open")
        print(f"  3. Type: ollama pull {RECOMMENDED_MODEL}")
        print("  4. Wait for download to complete")
        print("  5. Run: python backend/test_ollama.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
