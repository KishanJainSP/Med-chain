#!/usr/bin/env python3
"""
Debug the server analysis function directly
"""

import asyncio
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_server_analysis():
    """Debug the server analysis function step by step"""
    
    print("=" * 60)
    print("Debugging Server Analysis Function")
    print("=" * 60)
    
    # Import server functions
    try:
        import server
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        
        ROOT_DIR = Path(__file__).parent
        load_dotenv(ROOT_DIR / '.env')
        
        # Connect to database
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print("✓ Server imports successful")
        print("✓ Database connection established")
        
    except Exception as e:
        print(f"❌ Error with imports: {e}")
        return False
    
    # Test the retrieve_file function
    print("\nTesting retrieve_file function...")
    try:
        content = await server.retrieve_file("ipfs://debug_test_file")
        if content:
            print(f"✓ File retrieved: {len(content)} bytes")
            print(f"Content preview: {content[:100]}")
        else:
            print("❌ File not found - this is likely the issue!")
            print("The analysis is failing because retrieve_file returns None")
            
            # Check if file exists
            test_file_path = Path('uploads/debug_test_file')
            if test_file_path.exists():
                print(f"✓ File exists at: {test_file_path}")
                print("Issue: retrieve_file function not finding the file")
            else:
                print("❌ File doesn't exist")
                
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving file: {e}")
        return False
    
    # Test Ollama import in server context
    print("\nTesting Ollama import in server context...")
    try:
        from ollama_assistant import get_ollama_assistant
        ollama = get_ollama_assistant()
        print(f"✓ Ollama available: {ollama.available}")
        
        if not ollama.available:
            print("❌ Ollama not available in server context")
            return False
            
    except Exception as e:
        print(f"❌ Ollama import error in server context: {e}")
        return False
    
    # Test the extract_pdf_text function
    print("\nTesting PDF text extraction...")
    try:
        text = await server.extract_pdf_text(content)
        print(f"✓ Text extracted: {len(text) if text else 0} characters")
        if text:
            print(f"Text preview: {text[:200]}")
        else:
            print("⚠️  No text extracted (expected for non-PDF)")
            # For our test, use the raw content as text
            text = content.decode('utf-8')
            print(f"Using raw content as text: {len(text)} characters")
            
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return False
    
    # Test Ollama analysis with the extracted text
    print("\nTesting Ollama analysis with server context...")
    try:
        medical_prompt = f"""As a medical AI specialist, please analyze this medical record:

DOCUMENT TYPE: PDF
DOCUMENT TITLE: Blood Chemistry Panel - Debug Test
EXTRACTED CONTENT:
{text}

Please provide a detailed medical analysis in the following format:

SUMMARY:
[Provide a clear, professional summary]

KEY FINDINGS:
[List important findings]

RECOMMENDATIONS:
[Provide specific recommendations]"""

        response = ollama.answer_medical_question(
            question=medical_prompt,
            context={
                "document_type": "pdf",
                "document_title": "Blood Chemistry Panel - Debug Test",
                "extracted_text": text,
                "user_role": "medical_analysis"
            }
        )
        
        print(f"✓ Ollama analysis successful: {len(response)} characters")
        print("Analysis preview:")
        print("-" * 30)
        print(response[:200] + "..." if len(response) > 200 else response)
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama analysis failed: {e}")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    print("🔍 Debugging Server Analysis Function")
    
    success = asyncio.run(debug_server_analysis())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All components working - issue may be in analysis endpoint logic")
        print("The problem might be:")
        print("1. Error handling catching exceptions silently")
        print("2. Condition logic preventing Ollama usage")
        print("3. Database record format issues")
    else:
        print("❌ Found specific issue preventing Ollama analysis")
    print("=" * 60)