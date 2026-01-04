#!/usr/bin/env python3
"""
Debug the analysis endpoint to see why it's not using Ollama
"""

import requests
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_test_record():
    """Create a test medical record for analysis"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Create a test patient first
    test_patient = {
        "id": "test_patient_debug",
        "name": "Debug Patient",
        "wallet_address": "0xdebugpatient123",
        "date_of_birth": "1990-01-01",
        "gender": "Male",
        "blood_group": "O+",
        "phone": "555-0123",
        "email": "debug@test.com",
        "emergency_contact": "555-0124",
        "created_at": "2024-12-25T22:00:00Z"
    }
    
    # Insert or update patient
    await db.patients.update_one(
        {"id": "test_patient_debug"},
        {"$set": test_patient},
        upsert=True
    )
    
    # Create test medical record with sample content
    test_record = {
        "id": "test_record_debug",
        "patient_id": "test_patient_debug",
        "uploader_id": "test_patient_debug",
        "uploader_role": "patient",
        "title": "Blood Chemistry Panel - Debug Test",
        "description": "Test blood work for debugging analysis",
        "file_type": "pdf",
        "content_type": "application/pdf",
        "ipfs_hash": "ipfs://debug_test_file",
        "file_hash": "debug123hash",
        "size_bytes": 1024,
        "blockchain_tx": None,
        "is_confirmed": False,
        "created_at": "2024-12-25T22:00:00Z",
        "metadata": {}
    }
    
    # Insert or update record
    await db.records.update_one(
        {"id": "test_record_debug"},
        {"$set": test_record},
        upsert=True
    )
    
    # Create a fake file for testing
    test_file_content = b"""LABORATORY REPORT
Patient: Debug Patient
Date: 2024-12-25
Test: Comprehensive Metabolic Panel

RESULTS:
Glucose: 145 mg/dL (Normal: 70-100) HIGH
HbA1c: 6.8% (Normal: <5.7%) HIGH
Total Cholesterol: 220 mg/dL (Normal: <200) HIGH
LDL Cholesterol: 140 mg/dL (Normal: <100) HIGH
HDL Cholesterol: 35 mg/dL (Normal: >40) LOW
Triglycerides: 180 mg/dL (Normal: <150) HIGH
Creatinine: 1.2 mg/dL (Normal: 0.7-1.3) NORMAL

INTERPRETATION:
Multiple abnormal values detected requiring follow-up."""
    
    # Save test file
    from pathlib import Path
    uploads_dir = Path(__file__).parent / 'uploads'
    uploads_dir.mkdir(exist_ok=True)
    test_file_path = uploads_dir / 'debug_test_file'
    
    with open(test_file_path, 'wb') as f:
        f.write(test_file_content)
    
    client.close()
    
    print("✓ Test record created successfully")
    return "test_record_debug", "test_patient_debug"

async def test_analysis_endpoint():
    """Test the analysis endpoint directly"""
    
    print("=" * 60)
    print("Debugging Analysis Endpoint")
    print("=" * 60)
    
    # Create test record
    record_id, patient_id = await create_test_record()
    
    # Test the analysis endpoint
    base_url = "http://localhost:8000"
    
    try:
        print(f"Testing analysis for record: {record_id}")
        print(f"Patient ID: {patient_id}")
        
        # Call the analyze endpoint
        response = requests.post(
            f"{base_url}/api/records/{record_id}/analyze?requester_id={patient_id}",
            timeout=120  # Extended timeout for Ollama
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            analysis_data = response.json()
            
            print("\n" + "=" * 40)
            print("ANALYSIS RESULT")
            print("=" * 40)
            
            print(f"Ollama Powered: {analysis_data.get('ollama_powered', False)}")
            print(f"Summary Length: {len(analysis_data.get('summary', ''))}")
            print(f"Key Findings Count: {len(analysis_data.get('key_findings', []))}")
            print(f"Recommendations Count: {len(analysis_data.get('recommendations', []))}")
            
            print("\nSummary Preview:")
            print("-" * 30)
            summary = analysis_data.get('summary', 'No summary')
            print(summary[:300] + "..." if len(summary) > 300 else summary)
            
            print("\nKey Findings:")
            print("-" * 30)
            for i, finding in enumerate(analysis_data.get('key_findings', [])[:3]):
                print(f"{i+1}. {finding}")
            
            print("\nRecommendations:")
            print("-" * 30)
            for i, rec in enumerate(analysis_data.get('recommendations', [])[:3]):
                print(f"{i+1}. {rec}")
            
            # Check if it's using Ollama
            if analysis_data.get('ollama_powered'):
                print("\n✅ SUCCESS: Using Ollama for analysis!")
                return True
            else:
                print("\n❌ ISSUE: Not using Ollama - falling back to basic analysis")
                print("Checking why Ollama is not being used...")
                
                # Check Ollama availability
                try:
                    from ollama_assistant import get_ollama_assistant
                    ollama = get_ollama_assistant()
                    print(f"Ollama Available: {ollama.available}")
                    
                    if not ollama.available:
                        print("❌ Ollama is not available")
                        print("Please check:")
                        print("1. Ollama is running: ollama serve")
                        print("2. Model is installed: ollama pull llama3.2")
                        print("3. Check: python backend/check_ollama.py")
                    else:
                        print("✅ Ollama is available but not being used in analysis")
                        print("This suggests an error in the analysis code")
                        
                except Exception as e:
                    print(f"❌ Error checking Ollama: {e}")
                
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analysis: {e}")
        return False

def check_server_logs():
    """Check server logs for any errors"""
    print("\n" + "=" * 60)
    print("Checking Server Logs")
    print("=" * 60)
    
    # This would show recent server activity
    print("Check the server console for any error messages during analysis")
    print("Look for:")
    print("- Ollama import errors")
    print("- Analysis timeout errors") 
    print("- Database connection issues")
    print("- File retrieval errors")

if __name__ == "__main__":
    print("🔍 Debugging Analysis Endpoint")
    print()
    
    # Run the async test
    success = asyncio.run(test_analysis_endpoint())
    
    # Check server logs
    check_server_logs()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Analysis endpoint is working with Ollama!")
    else:
        print("❌ Analysis endpoint needs debugging")
        print("The issue is likely:")
        print("1. Ollama not available/running")
        print("2. Error in analysis code")
        print("3. Timeout or connection issue")
    print("=" * 60)