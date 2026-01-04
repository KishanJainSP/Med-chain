#!/usr/bin/env python3
"""
Debug Ollama analysis step by step
"""

import asyncio
from pathlib import Path

async def debug_ollama_step_by_step():
    """Debug each step of the Ollama analysis process"""
    
    print("=" * 60)
    print("Step-by-Step Ollama Analysis Debug")
    print("=" * 60)
    
    # Step 1: Check Ollama availability
    print("Step 1: Checking Ollama availability...")
    try:
        from ollama_assistant import get_ollama_assistant
        ollama = get_ollama_assistant()
        print(f"✓ Ollama Available: {ollama.available}")
        
        if not ollama.available:
            print("❌ Ollama not available - this is the issue!")
            return False
    except Exception as e:
        print(f"❌ Error importing Ollama: {e}")
        return False
    
    # Step 2: Test file retrieval
    print("\nStep 2: Testing file retrieval...")
    try:
        # Import the retrieve_file function from server
        import sys
        sys.path.append('.')
        
        # Read the test file directly
        test_file_path = Path('uploads/debug_test_file')
        if test_file_path.exists():
            with open(test_file_path, 'rb') as f:
                content = f.read()
            print(f"✓ File content retrieved: {len(content)} bytes")
            print(f"Content preview: {content[:100]}...")
        else:
            print("❌ Test file not found")
            return False
    except Exception as e:
        print(f"❌ Error retrieving file: {e}")
        return False
    
    # Step 3: Test PDF text extraction
    print("\nStep 3: Testing text extraction...")
    try:
        # Since our test file is plain text, simulate PDF extraction
        extracted_text = content.decode('utf-8')
        print(f"✓ Text extracted: {len(extracted_text)} characters")
        print(f"Text preview: {extracted_text[:200]}...")
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return False
    
    # Step 4: Test Ollama analysis directly
    print("\nStep 4: Testing Ollama analysis directly...")
    try:
        medical_prompt = f"""As a medical AI specialist, please analyze this medical record:

DOCUMENT TYPE: PDF
DOCUMENT TITLE: Blood Chemistry Panel - Debug Test
DOCUMENT DESCRIPTION: Test blood work for debugging analysis

EXTRACTED CONTENT:
{extracted_text}

Please provide a detailed medical analysis in the following format:

SUMMARY:
[Provide a clear, professional summary]

KEY FINDINGS:
[List the most important medical findings]

RECOMMENDATIONS:
[Provide specific medical recommendations]

Please write as a healthcare professional would."""

        print("Sending request to Ollama...")
        
        response = ollama.answer_medical_question(
            question=medical_prompt,
            context={
                "document_type": "pdf",
                "document_title": "Blood Chemistry Panel - Debug Test",
                "extracted_text": extracted_text,
                "user_role": "medical_analysis"
            }
        )
        
        print(f"✓ Ollama response received: {len(response)} characters")
        print("Response preview:")
        print("-" * 40)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Error with Ollama analysis: {e}")
        return False

def check_analysis_function():
    """Check if there's an issue with the analysis function itself"""
    
    print("\n" + "=" * 60)
    print("Checking Analysis Function Logic")
    print("=" * 60)
    
    try:
        # Import and check the server module
        import server
        
        # Check if the analyze_record function exists
        if hasattr(server, 'analyze_record'):
            print("✓ analyze_record function found")
        else:
            print("❌ analyze_record function not found")
            
        # Check imports in server
        try:
            from server import get_ollama_assistant
            print("✓ Ollama import in server works")
        except ImportError as e:
            print(f"❌ Ollama import issue in server: {e}")
            
    except Exception as e:
        print(f"❌ Error checking server module: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Ollama Analysis Process")
    
    # Run step-by-step debug
    success = asyncio.run(debug_ollama_step_by_step())
    
    # Check analysis function
    check_analysis_function()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Ollama analysis working - issue may be in server integration")
    else:
        print("❌ Found issue with Ollama analysis process")
    print("=" * 60)