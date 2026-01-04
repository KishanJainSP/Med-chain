"""
Quick Ollama test - just verify it's working
"""
import sys
import requests

def quick_test():
    print("=" * 60)
    print("Quick Ollama Test")
    print("=" * 60)
    
    # Test 1: Check service
    print("\n[1/3] Checking Ollama service...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✓ Ollama is running with {len(models)} model(s)")
                for m in models:
                    print(f"  - {m.get('name', 'unknown')}")
            else:
                print("✗ No models installed")
                return False
        else:
            print("✗ Ollama not responding")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Simple query
    print("\n[2/3] Testing simple query...")
    try:
        model_name = models[0].get("name", "").split(":")[0]
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "Say 'Hello MedChain' in one sentence.",
                "stream": False
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            print(f"✓ Ollama responded: {result[:50]}...")
        else:
            print("✗ Query failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Check MedChain integration
    print("\n[3/3] Checking MedChain integration...")
    try:
        from ollama_assistant import is_ollama_available
        if is_ollama_available():
            print("✓ MedChain can use Ollama")
        else:
            print("✗ MedChain cannot connect to Ollama")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Success
    print("\n" + "=" * 60)
    print("✓ SUCCESS! Ollama is working with MedChain")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Start server: python start_server.py")
    print("  2. Upload chest X-rays for AI analysis")
    print("  3. Get Ollama-enhanced summaries and recommendations")
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
