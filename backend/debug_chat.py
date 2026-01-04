"""
Debug script to test chat endpoint and verify Ollama is being used
"""
import sys
import requests
import json

def test_ollama_direct():
    """Test Ollama directly"""
    print("=" * 60)
    print("Testing Ollama Directly")
    print("=" * 60)
    
    try:
        # Test Ollama API directly
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": "Say 'Hello from Ollama' in one sentence.",
                "stream": False
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            print(f"\n✓ Ollama is working!")
            print(f"  Response: {result[:100]}...")
            return True
        else:
            print(f"\n✗ Ollama returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n✗ Ollama error: {e}")
        print("\nIs Ollama running?")
        print("  Check: python backend/check_ollama.py")
        return False

def test_ollama_assistant():
    """Test Ollama assistant module"""
    print("\n" + "=" * 60)
    print("Testing Ollama Assistant Module")
    print("=" * 60)
    
    try:
        from ollama_assistant import get_ollama_assistant
        
        ollama = get_ollama_assistant()
        
        if not ollama.available:
            print("\n✗ Ollama assistant says: NOT AVAILABLE")
            print(f"  Base URL: {ollama.base_url}")
            print(f"  Model: {ollama.model}")
            return False
        
        print(f"\n✓ Ollama assistant is available")
        print(f"  Base URL: {ollama.base_url}")
        print(f"  Model: {ollama.model}")
        
        # Test answer_medical_question
        print("\nTesting answer_medical_question()...")
        response = ollama.answer_medical_question(
            question="What is diabetes?",
            context={"user_role": "patient"}
        )
        
        if response and len(response) > 50:
            print(f"\n✓ Got response from Ollama!")
            print(f"  Length: {len(response)} characters")
            print(f"  Preview: {response[:150]}...")
            
            # Check if it's the generic help message
            if "I'm your MedChain AI Medical Assistant" in response:
                print("\n⚠ WARNING: Response contains generic help message!")
                print("  This should NOT happen - all responses should be from Ollama")
                return False
            else:
                print("\n✓ Response is from Ollama (not generic message)")
                return True
        else:
            print(f"\n✗ Response too short or empty: {response}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_endpoint():
    """Test the actual chat endpoint"""
    print("\n" + "=" * 60)
    print("Testing Chat Endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "What is diabetes?",
                "attached_record_ids": [],
                "user_id": "test_debug_user",
                "user_role": "patient"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "")
            ollama_powered = data.get("ollama_powered", False)
            
            print(f"\n✓ Chat endpoint responded")
            print(f"  Ollama powered: {ollama_powered}")
            print(f"  Response length: {len(bot_response)} characters")
            print(f"\n{'='*60}")
            print("Response Preview:")
            print(f"{'='*60}")
            print(bot_response[:300] + ("..." if len(bot_response) > 300 else ""))
            print(f"{'='*60}")
            
            # Check for generic messages
            if "I'm your MedChain AI Medical Assistant" in bot_response:
                print("\n✗ ERROR: Response contains generic help message!")
                print("  This means Ollama is NOT being used")
                print("\nPossible causes:")
                print("  1. Ollama not running")
                print("  2. Ollama not available when endpoint called")
                print("  3. Fallback code still being triggered")
                return False
            elif "Powered by Ollama AI" in bot_response or "powered by Ollama" in bot_response.lower():
                print("\n✓ SUCCESS: Response is from Ollama!")
                return True
            else:
                print("\n⚠ WARNING: Response doesn't have Ollama indicator")
                print("  But also doesn't have generic message")
                print("  Check if response is natural/conversational")
                return True
        else:
            print(f"\n✗ Chat endpoint returned status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to server")
        print("\nIs the server running?")
        print("  Run: python backend/start_server.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("MedChain Chat Debug Tool")
    print("=" * 60)
    
    results = []
    
    # Test 1: Ollama direct
    results.append(("Ollama Direct", test_ollama_direct()))
    
    # Test 2: Ollama assistant
    results.append(("Ollama Assistant", test_ollama_assistant()))
    
    # Test 3: Chat endpoint
    results.append(("Chat Endpoint", test_chat_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Debug Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed! Ollama is working correctly.")
    else:
        print("\n✗ Some tests failed. See details above.")
        print("\nTroubleshooting:")
        print("  1. Check Ollama: python backend/check_ollama.py")
        print("  2. Restart Ollama from Start menu")
        print("  3. Restart server: python backend/start_server.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
