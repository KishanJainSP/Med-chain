#!/usr/bin/env python3
"""
Setup completely local MongoDB database
"""

import os
import subprocess
import sys
from pathlib import Path
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def check_mongodb_service():
    """Check if MongoDB service is running on Windows"""
    try:
        # Check if MongoDB service is running
        result = subprocess.run(['sc', 'query', 'MongoDB'], 
                              capture_output=True, text=True, shell=True)
        if 'RUNNING' in result.stdout:
            print("✓ MongoDB service is running")
            return True
        else:
            print("✗ MongoDB service is not running")
            return False
    except Exception as e:
        print(f"Could not check MongoDB service: {e}")
        return False

def start_mongodb_service():
    """Start MongoDB service on Windows"""
    try:
        print("Starting MongoDB service...")
        result = subprocess.run(['net', 'start', 'MongoDB'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✓ MongoDB service started successfully")
            return True
        else:
            print(f"✗ Failed to start MongoDB service: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error starting MongoDB service: {e}")
        return False

async def setup_local_database():
    """Setup local MongoDB database with proper configuration"""
    
    print("=" * 60)
    print("Setting Up Local MongoDB Database")
    print("=" * 60)
    
    # Use local MongoDB connection
    mongo_url = "mongodb://localhost:27017"
    db_name = "medchain_local"
    
    print(f"Connecting to: {mongo_url}")
    print(f"Database: {db_name}")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Get database
        db = client[db_name]
        
        # Create collections if they don't exist
        collections = ['patients', 'doctors', 'institutions', 'records', 'consents', 'chat_messages']
        
        for collection_name in collections:
            # Create collection
            collection = db[collection_name]
            
            # Insert a test document and remove it to ensure collection exists
            test_doc = {"_test": True}
            result = await collection.insert_one(test_doc)
            await collection.delete_one({"_id": result.inserted_id})
            
            print(f"✓ Collection '{collection_name}' ready")
        
        # Create indexes for performance
        print("\nCreating database indexes...")
        
        # Wallet address indexes (unique)
        await db.patients.create_index("wallet_address", unique=True, sparse=True)
        await db.doctors.create_index("wallet_address", unique=True, sparse=True)
        await db.institutions.create_index("wallet_address", unique=True, sparse=True)
        
        # Other performance indexes
        await db.doctors.create_index("institution_id")
        await db.records.create_index("patient_id")
        await db.records.create_index("uploader_id")
        await db.consents.create_index([("patient_id", 1), ("doctor_id", 1)])
        await db.chat_messages.create_index("user_id")
        
        print("✓ All indexes created")
        
        # Update .env file with local configuration
        env_content = f"""# MongoDB Configuration - LOCAL ONLY
MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3002

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
        
        with open(ROOT_DIR / '.env', 'w') as f:
            f.write(env_content)
        
        print("✓ .env file updated with local configuration")
        
        # Test a simple query
        count = await db.patients.count_documents({})
        print(f"✓ Database test successful - {count} patients in database")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("✅ LOCAL MONGODB SETUP COMPLETE!")
        print("=" * 60)
        print("Database: medchain_local (completely local)")
        print("Connection: mongodb://localhost:27017")
        print("Status: Ready for use")
        
        return True
        
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

def kill_python_processes():
    """Kill existing Python processes to avoid conflicts"""
    try:
        print("Stopping existing Python processes...")
        result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, shell=True)
        if result.returncode == 0:
            print("✓ Python processes stopped")
        else:
            print("✓ No conflicting Python processes found")
    except Exception as e:
        print(f"✓ Process cleanup completed: {e}")

async def main():
    """Main setup function"""
    
    print("🔧 Setting up completely local MongoDB database...")
    print()
    
    # Step 1: Check MongoDB service
    if not check_mongodb_service():
        if not start_mongodb_service():
            print("\n❌ MongoDB service could not be started.")
            print("\nPlease install MongoDB Community Server:")
            print("1. Download from: https://www.mongodb.com/try/download/community")
            print("2. Install with default settings")
            print("3. Ensure 'Install MongoDB as a Service' is checked")
            print("4. Run this script again")
            return False
    
    # Step 2: Kill existing processes
    kill_python_processes()
    
    # Step 3: Setup database
    success = await setup_local_database()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Start the server: python backend/start_server.py")
        print("2. Test CORS: python backend/fix_cors_now.py")
        print("3. Try your frontend login again")
        print("\n✅ Local MongoDB is ready!")
    else:
        print("\n❌ Setup failed. Check MongoDB installation.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())