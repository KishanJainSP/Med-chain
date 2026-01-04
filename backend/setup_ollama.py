"""
Setup script for Ollama integration with MedChain
Downloads and configures Ollama for medical AI assistance
"""
import os
import sys
import platform
import subprocess
import requests
import time

def check_ollama_installed():
    """Check if Ollama is already installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Ollama is already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    return False

def get_download_instructions():
    """Get platform-specific download instructions"""
    system = platform.system()
    
    instructions = {
        "Windows": """
To install Ollama on Windows:
1. Download from: https://ollama.com/download/windows
2. Run the installer (OllamaSetup.exe)
3. Follow the installation wizard
4. Ollama will start automatically after installation
        """,
        "Darwin": """
To install Ollama on macOS:
1. Download from: https://ollama.com/download/mac
2. Open the downloaded .dmg file
3. Drag Ollama to Applications
4. Open Ollama from Applications
        """,
        "Linux": """
To install Ollama on Linux:
Run this command in your terminal:
curl -fsSL https://ollama.com/install.sh | sh
        """
    }
    
    return instructions.get(system, "Visit https://ollama.com/download for installation instructions")

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama service is running")
            return True
    except:
        pass
    return False

def start_ollama_service():
    """Attempt to start Ollama service"""
    system = platform.system()
    
    print("Attempting to start Ollama service...")
    
    if system == "Windows":
        print("On Windows, Ollama should start automatically.")
        print("If not, search for 'Ollama' in Start menu and run it.")
    elif system == "Darwin":
        print("On macOS, open Ollama from Applications folder.")
    elif system == "Linux":
        try:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
        except:
            print("Could not start Ollama automatically. Run: ollama serve")
    
    return check_ollama_running()

def pull_model(model_name="llama3.2"):
    """Pull the specified Ollama model"""
    print(f"\nPulling Ollama model: {model_name}")
    print("This may take a few minutes depending on your internet connection...")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Successfully pulled model: {model_name}")
            return True
        else:
            print(f"✗ Failed to pull model: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error pulling model: {e}")
        return False

def list_available_models():
    """List available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("\n✓ Available Ollama models:")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) / (1024**3)  # Convert to GB
                    print(f"  - {name} ({size:.2f} GB)")
                return True
            else:
                print("\n⚠ No models installed yet")
                return False
    except Exception as e:
        print(f"✗ Could not list models: {e}")
        return False

def test_ollama_integration():
    """Test Ollama integration with MedChain"""
    print("\nTesting Ollama integration with MedChain...")
    
    try:
        from ollama_assistant import get_ollama_assistant
        
        assistant = get_ollama_assistant()
        
        if assistant.available:
            print("✓ Ollama assistant initialized successfully")
            
            # Test simple query
            test_response = assistant.generate_response(
                "What is diabetes?",
                system_prompt="You are a medical AI assistant. Provide a brief one-sentence answer."
            )
            
            if test_response:
                print("✓ Ollama is responding correctly")
                print(f"  Test response: {test_response[:100]}...")
                return True
            else:
                print("✗ Ollama not responding")
                return False
        else:
            print("✗ Ollama assistant not available")
            return False
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("MedChain Ollama Setup")
    print("=" * 60)
    
    # Step 1: Check if Ollama is installed
    print("\n[Step 1] Checking Ollama installation...")
    if not check_ollama_installed():
        print("\n✗ Ollama is not installed")
        print(get_download_instructions())
        print("\nAfter installing Ollama, run this script again.")
        return False
    
    # Step 2: Check if Ollama service is running
    print("\n[Step 2] Checking Ollama service...")
    if not check_ollama_running():
        print("✗ Ollama service is not running")
        if not start_ollama_service():
            print("\nPlease start Ollama manually and run this script again.")
            return False
    
    # Step 3: List available models
    print("\n[Step 3] Checking available models...")
    has_models = list_available_models()
    
    # Step 4: Pull recommended model if needed
    if not has_models:
        print("\n[Step 4] Installing recommended model...")
        print("Recommended models:")
        print("  - llama3.2 (2GB) - Fast, good for general use")
        print("  - llama3.2:1b (1.3GB) - Smallest, fastest")
        print("  - llama3.1 (4.7GB) - More capable, slower")
        
        model_choice = input("\nEnter model name (or press Enter for llama3.2): ").strip()
        if not model_choice:
            model_choice = "llama3.2"
        
        if not pull_model(model_choice):
            print("\n✗ Failed to pull model. You can try manually: ollama pull " + model_choice)
            return False
    
    # Step 5: Test integration
    print("\n[Step 5] Testing MedChain integration...")
    if test_ollama_integration():
        print("\n" + "=" * 60)
        print("✓ SUCCESS! Ollama is ready to use with MedChain")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Start your MedChain backend server")
        print("  2. Upload medical images for AI analysis")
        print("  3. Get AI-powered summaries and recommendations")
        print("\nOllama will enhance your medical AI with:")
        print("  - Intelligent summaries of EfficientNet predictions")
        print("  - Contextual recommendations")
        print("  - Natural language explanations")
        return True
    else:
        print("\n✗ Integration test failed")
        print("Please check the error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
