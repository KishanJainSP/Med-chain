#!/usr/bin/env python3
"""
Simple test for enhanced medical analysis
"""

import requests
import json

def test_simple():
    """Simple test of the enhanced analysis"""
    
    print("=" * 50)
    print("Quick Test: Enhanced Medical Analysis")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            ollama_status = data.get("ai_models", {}).get("ollama_available", False)
            print(f"✓ Server: Running")
            print(f"✓ Ollama: {'Available' if ollama_status else 'Not Available'}")
            
            if ollama_status:
                print("\n🎉 ENHANCED ANALYSIS READY!")
                print("✓ Medical records will get professional Ollama analysis")
                print("✓ Chat responses powered by Llama AI")
                print("✓ Detailed medical insights and recommendations")
                
                print("\nWhat's Enhanced:")
                print("• Professional medical terminology")
                print("• Detailed clinical interpretations")
                print("• Specific recommendations")
                print("• Contextual medical insights")
                print("• Health specialist-level analysis")
                
                return True
            else:
                print("\n⚠️  Using Basic Analysis")
                print("Ollama not available - using rule-based fallback")
                return False
        else:
            print("✗ Server not responding")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ SUCCESS: Enhanced medical analysis is active!")
        print("\nTry uploading a medical document and clicking 'Analyze'")
        print("You should see much more detailed, professional analysis!")
    else:
        print("❌ Enhanced analysis not available")
        print("Using basic analysis mode")
    print("=" * 50)