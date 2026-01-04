"""
Quick test script for Ollama integration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("=" * 60)
    print("Testing Ollama Connection")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Ollama is not available")
        print("\nPlease ensure:")
        print("  1. Ollama is installed")
        print("  2. Ollama service is running")
        print("  3. At least one model is pulled (e.g., ollama pull llama3.2)")
        print("\nRun: python setup_ollama.py")
        return False
    
    print(f"✓ Ollama is available")
    print(f"  Base URL: {assistant.base_url}")
    print(f"  Model: {assistant.model}")
    return True

def test_simple_query():
    """Test simple medical query"""
    print("\n" + "=" * 60)
    print("Testing Simple Medical Query")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Skipping (Ollama not available)")
        return False
    
    query = "What is hypertension?"
    print(f"\nQuery: {query}")
    print("\nGenerating response...")
    
    response = assistant.generate_response(
        query,
        system_prompt="You are a medical AI. Provide a brief 2-sentence answer."
    )
    
    if response:
        print(f"\n✓ Response received:")
        print(f"  {response}")
        return True
    else:
        print("✗ No response received")
        return False

def test_efficientnet_enhancement():
    """Test EfficientNet result enhancement"""
    print("\n" + "=" * 60)
    print("Testing EfficientNet Enhancement")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Skipping (Ollama not available)")
        return False
    
    # Mock EfficientNet output
    mock_output = {
        "success": True,
        "model": "Fine-tuned EfficientNet",
        "confidence": 0.75,
        "findings": [
            "Pneumonia: 75% confidence",
            "Infiltration: 45% confidence"
        ],
        "recommendations": [
            "Consider antibiotic treatment if bacterial infection suspected"
        ],
        "all_predictions": {
            "Pneumonia": 0.75,
            "Infiltration": 0.45,
            "Atelectasis": 0.12,
            "Cardiomegaly": 0.08
        }
    }
    
    print("\nMock EfficientNet Output:")
    print(f"  Findings: {mock_output['findings']}")
    print("\nEnhancing with Ollama...")
    
    enhanced = assistant.analyze_efficientnet_results(mock_output)
    
    if enhanced.get("ollama_summary"):
        print(f"\n✓ Ollama Summary Generated:")
        print(f"  {enhanced['ollama_summary'][:200]}...")
        return True
    else:
        print("✗ No Ollama summary generated")
        return False

def test_text_classification_enhancement():
    """Test text classification enhancement"""
    print("\n" + "=" * 60)
    print("Testing Text Classification Enhancement")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Skipping (Ollama not available)")
        return False
    
    # Mock text classifier output
    mock_output = {
        "success": True,
        "model": "Fine-tuned Text Classifier",
        "predicted_category": "Symptom",
        "confidence": 0.92,
        "all_predictions": {
            "Symptom": 0.92,
            "Diagnosis": 0.05,
            "Medication": 0.02,
            "Test Result": 0.01,
            "Treatment": 0.00
        }
    }
    
    original_text = "Patient experiencing severe chest pain radiating to left arm"
    
    print(f"\nOriginal Text: {original_text}")
    print(f"Classification: {mock_output['predicted_category']} ({mock_output['confidence']:.1%})")
    print("\nEnhancing with Ollama...")
    
    enhanced = assistant.analyze_text_classification(mock_output, original_text)
    
    if enhanced.get("ollama_insights"):
        print(f"\n✓ Ollama Insights Generated:")
        print(f"  {enhanced['ollama_insights'][:200]}...")
        return True
    else:
        print("✗ No Ollama insights generated")
        return False

def test_comprehensive_summary():
    """Test comprehensive summary generation"""
    print("\n" + "=" * 60)
    print("Testing Comprehensive Summary")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Skipping (Ollama not available)")
        return False
    
    # Mock data
    image_analysis = {
        "success": True,
        "model": "EfficientNet",
        "confidence": 0.75,
        "findings": ["Pneumonia: 75% confidence"]
    }
    
    text_analysis = {
        "success": True,
        "predicted_category": "Symptom",
        "confidence": 0.92
    }
    
    patient_query = "What do my chest X-ray results mean?"
    
    print(f"\nPatient Query: {patient_query}")
    print("Generating comprehensive summary...")
    
    summary = assistant.generate_comprehensive_summary(
        image_analysis=image_analysis,
        text_analysis=text_analysis,
        patient_query=patient_query
    )
    
    if summary and len(summary) > 50:
        print(f"\n✓ Comprehensive Summary Generated:")
        print(f"  {summary[:300]}...")
        return True
    else:
        print("✗ No comprehensive summary generated")
        return False

def test_recommendations():
    """Test recommendation generation"""
    print("\n" + "=" * 60)
    print("Testing Recommendation Generation")
    print("=" * 60)
    
    from ollama_assistant import get_ollama_assistant
    
    assistant = get_ollama_assistant()
    
    if not assistant.available:
        print("✗ Skipping (Ollama not available)")
        return False
    
    findings = [
        "Pneumonia detected with 75% confidence",
        "Elevated blood pressure: 150/95 mmHg"
    ]
    
    print(f"\nFindings:")
    for finding in findings:
        print(f"  - {finding}")
    
    print("\nGenerating recommendations...")
    
    recommendations = assistant.get_medical_recommendations(
        findings=findings,
        context="Patient has history of hypertension"
    )
    
    if recommendations and len(recommendations) > 0:
        print(f"\n✓ Recommendations Generated:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        return True
    else:
        print("✗ No recommendations generated")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MedChain Ollama Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Connection", test_ollama_connection),
        ("Simple Query", test_simple_query),
        ("EfficientNet Enhancement", test_efficientnet_enhancement),
        ("Text Classification Enhancement", test_text_classification_enhancement),
        ("Comprehensive Summary", test_comprehensive_summary),
        ("Recommendations", test_recommendations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Ollama integration is working correctly.")
        return True
    elif passed > 0:
        print("\n⚠ Some tests passed. Ollama is partially working.")
        return True
    else:
        print("\n✗ All tests failed. Please run: python setup_ollama.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
