#!/usr/bin/env python3
"""
Test the enhanced medical analysis with Ollama integration
"""

import requests
import json

def test_enhanced_analysis():
    """Test the enhanced medical record analysis"""
    
    print("=" * 60)
    print("Testing Enhanced Medical Analysis with Ollama")
    print("=" * 60)
    
    # Test the analyze endpoint (this would normally be called after uploading a record)
    base_url = "http://localhost:8000"
    
    # First, let's test if Ollama is available
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            ollama_status = health_data.get("ai_models", {}).get("ollama_available", False)
            print(f"Server Status: ✓ Running")
            print(f"Ollama Status: {'✓ Available' if ollama_status else '✗ Not Available'}")
            print()
            
            if not ollama_status:
                print("⚠️  Ollama not available - analysis will use fallback mode")
                print("To enable Ollama:")
                print("1. Ensure Ollama is running")
                print("2. Check: python backend/check_ollama.py")
                print("3. Install model: python backend/install_ollama_model.py")
                return False
            else:
                print("✓ Ollama is available - enhanced analysis ready!")
                
        else:
            print("✗ Server not responding")
            return False
            
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        return False
    
    # Test chat endpoint with medical question
    print("\n" + "=" * 60)
    print("Testing Enhanced Chat with Medical Context")
    print("=" * 60)
    
    try:
        chat_payload = {
            "message": "I have a blood test report showing elevated glucose levels. What should I be concerned about?",
            "attached_record_ids": [],
            "user_id": "test_patient_123",
            "user_role": "patient"
        }
        
        print("Sending medical question to chat endpoint...")
        print(f"Question: {chat_payload['message']}")
        print()
        
        chat_response = requests.post(
            f"{base_url}/api/chat",
            json=chat_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            response_text = chat_data.get("response", "")
            ollama_powered = chat_data.get("ollama_powered", False)
            
            print("✓ Chat Response Received")
            print(f"Ollama Powered: {'✓ Yes' if ollama_powered else '✗ No'}")
            print()
            print("Response Preview:")
            print("-" * 40)
            print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
            print("-" * 40)
            
            # Check if response is more detailed than generic
            if len(response_text) > 100 and ("glucose" in response_text.lower() or "blood" in response_text.lower()):
                print("✓ Response appears to be contextually relevant")
            else:
                print("⚠️  Response may be generic")
                
            return True
            
        else:
            print(f"✗ Chat request failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing chat: {e}")
        return False

def test_ollama_direct():
    """Test Ollama assistant directly"""
    
    print("\n" + "=" * 60)
    print("Testing Ollama Assistant Directly")
    print("=" * 60)
    
    try:
        from ollama_assistant import get_ollama_assistant
        
        ollama = get_ollama_assistant()
        
        if not ollama.available:
            print("✗ Ollama not available")
            return False
        
        print("✓ Ollama assistant loaded")
        
        # Test medical analysis
        test_prompt = """As a medical AI specialist, please analyze this blood test report:

DOCUMENT TYPE: PDF
DOCUMENT TITLE: Blood Chemistry Panel
DOCUMENT DESCRIPTION: Routine blood work

EXTRACTED CONTENT:
Patient: John Doe
Date: 2024-12-25
Glucose: 145 mg/dL (Normal: 70-100)
HbA1c: 6.8% (Normal: <5.7%)
Total Cholesterol: 220 mg/dL (Normal: <200)
LDL: 140 mg/dL (Normal: <100)
HDL: 35 mg/dL (Normal: >40 for men)

Please provide a detailed medical analysis."""

        print("Testing medical analysis prompt...")
        
        response = ollama.answer_medical_question(
            test_prompt,
            {"user_role": "medical_analysis"}
        )
        
        print("✓ Ollama analysis completed")
        print()
        print("Analysis Preview:")
        print("-" * 40)
        print(response[:400] + "..." if len(response) > 400 else response)
        print("-" * 40)
        
        # Check if response contains medical insights
        response_lower = response.lower()
        medical_terms = ["glucose", "diabetes", "cholesterol", "cardiovascular", "hba1c"]
        found_terms = [term for term in medical_terms if term in response_lower]
        
        if len(found_terms) >= 3:
            print(f"✓ Response contains relevant medical terms: {', '.join(found_terms)}")
            return True
        else:
            print(f"⚠️  Response may lack medical depth. Found terms: {', '.join(found_terms)}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing Ollama directly: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Testing Enhanced Medical Analysis System")
    print()
    
    # Test server and Ollama availability
    server_ok = test_enhanced_analysis()
    
    # Test Ollama directly
    ollama_ok = test_ollama_direct()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if server_ok and ollama_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✓ Enhanced medical analysis is working")
        print("✓ Ollama integration successful")
        print("✓ Medical records will get professional analysis")
        print("\nYour medical analysis should now be much more detailed and professional!")
    elif server_ok:
        print("⚠️  PARTIAL SUCCESS")
        print("✓ Server is working")
        print("✗ Ollama integration needs attention")
        print("\nBasic analysis available, but enhanced features need Ollama setup")
    else:
        print("❌ TESTS FAILED")
        print("✗ Server or Ollama issues detected")
        print("\nPlease check server status and Ollama installation")
    
    print("=" * 60)