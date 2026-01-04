"""
Final test to verify chat is using ONLY Ollama
"""
import sys
import requests
import time

def test_ollama_status():
    """Check if Ollama is running"""
    print("=" * 60)
    print("Step 1: Checking Ollama Status")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"\n✓ Ollama is running")
                print(f"  Models: {[m.get('name') for m in models]}")
                return True
            else:
                print("\n✗ Ollama running but no models installed")
                return False
        else:
            print(f"\n✗ Ollama returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n✗ Ollama not available: {e}")
        print("\nFix: Open Ollama from Start menu")
        return False

def test_chat_simple():
    """Test with simple question"""
    print("\n" + "=" * 60)
    print("Step 2: Testing Simple Question")
    print("=" * 60)
    
    print("\nSending: 'Hello'")
    print("Waiting for response (may take up to 60 seconds)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "Hello",
                "attached_record_ids": [],
                "user_id": "test_final_user",
                "user_role": "patient"
            },
            timeout=90
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "")
            ollama_powered = data.get("ollama_powered", False)
            
            print(f"\n✓ Response received in {elapsed:.1f} seconds")
            print(f"  Ollama powered: {ollama_powered}")
            print(f"\n{'='*60}")
            print("Response:")
            print(f"{'='*60}")
            print(bot_response)
            print(f"{'='*60}")
            
            # Check for bad patterns
            bad_patterns = [
                "I'm your MedChain AI Medical Assistant powered by",
                "EfficientNet for medical image analysis",
                "ClinicalBERT for medical text",
                "I can help you with:",
                "To get started:"
            ]
            
            has_bad_pattern = any(pattern in bot_response for pattern in bad_patterns)
            
            if has_bad_pattern:
                print("\n✗ FAIL: Response contains pre-defined message!")
                print("  This should NOT happen")
                return False
            elif ollama_powered and "Powered by Ollama" in bot_response:
                print("\n✓ PASS: Response is from Ollama!")
                return True
            else:
                print("\n⚠ WARNING: Response format unexpected")
                return False
        else:
            print(f"\n✗ Server returned status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n✗ Request timed out after 90 seconds")
        print("  Ollama may be too slow or stuck")
        return False
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to server")
        print("\nFix: Run 'python backend/start_server.py'")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def test_chat_medical():
    """Test with medical question"""
    print("\n" + "=" * 60)
    print("Step 3: Testing Medical Question")
    print("=" * 60)
    
    print("\nSending: 'What is diabetes?'")
    print("Waiting for response...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "What is diabetes?",
                "attached_record_ids": [],
                "user_id": "test_final_user",
                "user_role": "patient"
            },
            timeout=90
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "")
            
            print(f"\n✓ Response received in {elapsed:.1f} seconds")
            print(f"\n{'='*60}")
            print("Response Preview (first 300 chars):")
            print(f"{'='*60}")
            print(bot_response[:300] + "...")
            print(f"{'='*60}")
            
            # Check quality
            if len(bot_response) < 100:
                print("\n⚠ WARNING: Response is very short")
                return False
            elif "I'm your MedChain AI Medical Assistant" in bot_response:
                print("\n✗ FAIL: Pre-defined message detected!")
                return False
            elif "Powered by Ollama" in bot_response:
                print("\n✓ PASS: Natural Ollama response!")
                return True
            else:
                print("\n⚠ WARNING: Response format unexpected")
                return False
        else:
            print(f"\n✗ Server returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("FINAL CHAT TEST - Ollama Only")
    print("=" * 60)
    
    # Test 1: Ollama status
    if not test_ollama_status():
        print("\n✗ Ollama is not running. Cannot proceed.")
        print("\nFix:")
        print("  1. Open Ollama from Start menu")
        print("  2. Wait 10 seconds")
        print("  3. Run this test again")
        return False
    
    # Test 2: Simple question
    if not test_chat_simple():
        print("\n✗ Simple question test failed")
        return False
    
    # Test 3: Medical question
    if not test_chat_medical():
        print("\n✗ Medical question test failed")
        return False
    
    # Success
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nChat is working correctly:")
    print("  ✓ Ollama is running")
    print("  ✓ Responses come from Ollama")
    print("  ✓ No pre-defined messages")
    print("  ✓ Natural conversational responses")
    print("\nYou can now use the chat in your UI!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
