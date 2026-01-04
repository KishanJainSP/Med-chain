#!/usr/bin/env python3
"""
Debug the exact flow of the analysis function
"""

import requests
import json

def test_analysis_with_logging():
    """Test analysis and check server logs"""
    
    print("=" * 60)
    print("Testing Analysis with Detailed Logging")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test the analysis endpoint
    try:
        print("Sending analysis request...")
        
        response = requests.post(
            f"{base_url}/api/records/test_record_debug/analyze?requester_id=test_patient_debug",
            timeout=120
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\nResponse Analysis:")
            print(f"- Ollama Powered: {data.get('ollama_powered', 'Not set')}")
            print(f"- Summary exists: {data.get('summary') is not None}")
            print(f"- Key findings count: {len(data.get('key_findings', []))}")
            print(f"- Recommendations count: {len(data.get('recommendations', []))}")
            print(f"- Analysis field exists: {data.get('analysis') is not None}")
            
            # Show actual content
            if data.get('summary'):
                print(f"\nSummary preview: {data['summary'][:200]}...")
            
            if data.get('key_findings'):
                print(f"\nFirst key finding: {data['key_findings'][0] if data['key_findings'] else 'None'}")
            
            if data.get('recommendations'):
                print(f"\nFirst recommendation: {data['recommendations'][0] if data['recommendations'] else 'None'}")
            
            # Check if it contains Ollama indicators
            full_response = json.dumps(data, indent=2)
            if "ollama" in full_response.lower() or "powered by" in full_response.lower():
                print("\n✅ Found Ollama indicators in response")
            else:
                print("\n❌ No Ollama indicators found")
                
            return data.get('ollama_powered', False)
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Analysis Flow")
    
    success = test_analysis_with_logging()
    
    print("\n" + "=" * 60)
    print("Check the server console output above for detailed logs")
    print("Look for messages starting with:")
    print("- 'Starting Ollama analysis for record'")
    print("- 'Extracted text length'")
    print("- 'Document type'")
    print("- 'Analysis type determined'")
    print("- 'Ollama analysis completed'")
    print("=" * 60)
    
    if success:
        print("✅ Ollama analysis working!")
    else:
        print("❌ Still using fallback analysis")
        print("Check server logs for specific error messages")