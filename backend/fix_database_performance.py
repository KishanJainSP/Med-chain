#!/usr/bin/env python3
"""
Fix database performance by adding indexes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_indexes():
    """Create database indexes for better performance"""
    
    print("=" * 60)
    print("Creating Database Indexes for Performance")
    print("=" * 60)
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create indexes for wallet_address fields (most important for user lookup)
        print("Creating wallet_address indexes...")
        
        # Patients collection
        await db.patients.create_index("wallet_address", unique=True)
        print("✓ patients.wallet_address index created")
        
        # Doctors collection  
        await db.doctors.create_index("wallet_address", unique=True)
        print("✓ doctors.wallet_address index created")
        
        # Institutions collection
        await db.institutions.create_index("wallet_address", unique=True)
        print("✓ institutions.wallet_address index created")
        
        # Other useful indexes
        await db.doctors.create_index("institution_id")
        print("✓ doctors.institution_id index created")
        
        await db.records.create_index("patient_id")
        print("✓ records.patient_id index created")
        
        await db.records.create_index("uploader_id")
        print("✓ records.uploader_id index created")
        
        await db.consents.create_index([("patient_id", 1), ("doctor_id", 1)])
        print("✓ consents compound index created")
        
        await db.chat_messages.create_index("user_id")
        print("✓ chat_messages.user_id index created")
        
        print()
        print("✓ All indexes created successfully!")
        print("✓ Database queries should be much faster now")
        
    except Exception as e:
        print(f"✗ Error creating indexes: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())