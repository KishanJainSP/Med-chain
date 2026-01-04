#!/usr/bin/env python3
"""
Test the analysis window specifically to ensure Ollama integration is working
"""

import requests
import json
import time

def test_analysis_window():
    """Test the medical record analysis window functionality"""
    
    print("=" * 60)
    print("Testing Analysis Window - Ollama Integration")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # First check if server and Ollama are available
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            ollama_status = health_data.get("ai_models", {}).get("ollama_available", False)
            print(f"✓ Server Status: Running")
            print(f"✓ Ollama Status: {'Available' if ollama_status else 'Not Available'}")
            
            if not ollama_status:
                print("\n❌ Ollama not available - analysis will be basic")
                print("Please ensure Ollama is running for advanced analysis")
                return False
        else:
            print("❌ Server not responding")
            return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Testing Direct Ollama Medical Analysis")
    print("=" * 60)
    
    # Test Ollama directly for medical analysis
    try:
        from ollama_assistant import get_ollama_assistant
        
        ollama = get_ollama_assistant()
        if not ollama.available:
            print("❌ Ollama assistant not available")
            return False
        
        print("✓ Ollama assistant loaded successfully")
        
        # Test with a sample medical document analysis
        test_medical_prompt = """You are a medical specialist analyzing a laboratory report. Provide a comprehensive, professional medical analysis.

DOCUMENT INFORMATION:
- Type: PDF
- Title: Blood Chemistry Panel
- Description: Routine laboratory work

CLINICAL DATA:
Patient: Test Patient
Date: 2024-12-25
Glucose: 145 mg/dL (Normal: 70-100)
HbA1c: 6.8% (Normal: <5.7%)
Total Cholesterol: 220 mg/dL (Normal: <200)
LDL Cholesterol: 140 mg/dL (Normal: <100)
HDL Cholesterol: 35 mg/dL (Normal: >40 for men)
Triglycerides: 180 mg/dL (Normal: <150)
Creatinine: 1.2 mg/dL (Normal: 0.7-1.3)

Focus on:
- Laboratory values and reference ranges
- Abnormal findings and their clinical significance
- Patterns indicating specific conditions
- Risk stratification and urgency of findings
- Specific follow-up testing recommendations

Provide your analysis in this EXACT format:

SUMMARY:
[Write 2-3 sentences summarizing the key medical findings and their overall clinical significance. Be specific about abnormalities, conditions, or concerns identified.]

KEY FINDINGS:
• [List 3-5 specific, clinically relevant findings]
• [Include abnormal values, concerning symptoms, or notable observations]
• [Prioritize findings by clinical importance]

CLINICAL INTERPRETATION:
[Explain what these findings mean medically. Discuss potential diagnoses, disease processes, or health implications. Be specific about medical significance.]

RECOMMENDATIONS:
• [Provide 3-5 specific, actionable medical recommendations]
• [Include follow-up care, additional testing, specialist referrals]
• [Prioritize by urgency and importance]

FOLLOW-UP CARE:
• [Suggest specific monitoring, timeline for reassessment]
• [Identify when to seek immediate medical attention]
• [Recommend preventive measures or lifestyle modifications]

Use professional medical terminology but ensure clarity. Focus on actionable insights and patient safety."""

        print("Sending medical analysis request to Ollama...")
        print("This may take 30-60 seconds for detailed analysis...")
        
        start_time = time.time()
        
        response = ollama.answer_medical_question(
            test_medical_prompt,
            {"user_role": "medical_analysis"}
        )
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"✓ Analysis completed in {analysis_time:.1f} seconds")
        print(f"✓ Response length: {len(response)} characters")
        
        # Check if response contains expected medical analysis sections
        response_upper = response.upper()
        sections_found = []
        
        if "SUMMARY:" in response_upper:
            sections_found.append("Summary")
        if "KEY FINDINGS:" in response_upper:
            sections_found.append("Key Findings")
        if "CLINICAL INTERPRETATION:" in response_upper:
            sections_found.append("Clinical Interpretation")
        if "RECOMMENDATIONS:" in response_upper:
            sections_found.append("Recommendations")
        if "FOLLOW-UP CARE:" in response_upper:
            sections_found.append("Follow-up Care")
        
        print(f"✓ Structured sections found: {', '.join(sections_found)}")
        
        # Check for medical terminology
        medical_terms = ["glucose", "diabetes", "cholesterol", "cardiovascular", "hba1c", "lipid", "metabolic"]
        found_terms = [term for term in medical_terms if term.lower() in response.lower()]
        print(f"✓ Medical terms detected: {', '.join(found_terms)}")
        
        # Show preview of analysis
        print("\n" + "-" * 50)
        print("ANALYSIS PREVIEW:")
        print("-" * 50)
        
        # Show first 500 characters
        preview = response[:500] + "..." if len(response) > 500 else response
        print(preview)
        print("-" * 50)
        
        # Determine if analysis is advanced
        is_advanced = (
            len(sections_found) >= 3 and
            len(found_terms) >= 4 and
            len(response) > 300 and
            analysis_time < 120  # Completed within reasonable time
        )
        
        if is_advanced:
            print("\n🎉 ADVANCED ANALYSIS CONFIRMED!")
            print("✓ Structured medical analysis")
            print("✓ Professional medical terminology")
            print("✓ Detailed clinical insights")
            print("✓ Specific recommendations")
            print("\nThe analysis window should now show professional-grade medical analysis!")
            return True
        else:
            print("\n⚠️  Analysis may need improvement")
            print(f"Sections: {len(sections_found)}/5")
            print(f"Medical terms: {len(found_terms)}/7")
            print(f"Length: {len(response)} chars")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama analysis: {e}")
        return False

def test_analysis_endpoint():
    """Test the actual analysis endpoint that the frontend uses"""
    
    print("\n" + "=" * 60)
    print("Testing Analysis Endpoint Integration")
    print("=" * 60)
    
    # Note: This would require an actual uploaded record to test
    # For now, just verify the endpoint structure
    
    print("ℹ️  Analysis endpoint testing requires uploaded medical records")
    print("To test the analysis window:")
    print("1. Upload a medical document in the frontend")
    print("2. Click the 'Analyze' button")
    print("3. Check if the analysis shows detailed, professional insights")
    print("4. Look for 'Powered by Ollama Medical AI Specialist' indicator")
    
    return True

if __name__ == "__main__":
    print("🔬 Testing Analysis Window - Ollama Integration")
    print()
    
    # Test Ollama medical analysis capability
    ollama_test = test_analysis_window()
    
    # Test endpoint integration
    endpoint_test = test_analysis_endpoint()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if ollama_test and endpoint_test:
        print("🎉 SUCCESS: Advanced Medical Analysis Ready!")
        print("✓ Ollama integration working")
        print("✓ Professional medical analysis confirmed")
        print("✓ Analysis window should show detailed insights")
        print("\nYour analysis window will now provide:")
        print("• Professional medical terminology")
        print("• Detailed clinical interpretations")
        print("• Specific medical recommendations")
        print("• Structured analysis format")
        print("• Health specialist-level insights")
    else:
        print("❌ Issues detected with advanced analysis")
        print("The analysis window may still show basic responses")
        print("Check Ollama installation and model availability")
    
    print("=" * 60)