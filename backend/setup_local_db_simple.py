#!/usr/bin/env python3
"""
Simple local MongoDB setup
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

async def setup_local_db():
    """Setup local MongoDB database"""
    
    print("=" * 50)
    print("Setting Up Local MongoDB")
    print("=" * 50)
    
    # Local MongoDB connection
    mongo_url = "mongodb://localhost:27017"
    db_name = "medchain_local"
    
    print(f"Connecting to: {mongo_url}")
    print(f"Database: {db_name}")
    
    try:
        # Connect with short timeout
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=3000)
        
        # Test connection
        await client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Get database
        db = client[db_name]
        
        # Create collections
        collections = ['patients', 'doctors', 'institutions', 'records', 'consents', 'chat_messages']
        
        for collection_name in collections:
            collection = db[collection_name]
            # Ensure collection exists
            await collection.create_index("_id")
            print(f"✓ Collection '{collection_name}' ready")
        
        # Create wallet address indexes
        print("\nCreating indexes...")
        await db.patients.create_index("wallet_address", unique=True, sparse=True)
        await db.doctors.create_index("wallet_address", unique=True, sparse=True) 
        await db.institutions.create_index("wallet_address", unique=True, sparse=True)
        print("✓ Wallet indexes created")
        
        # Test query
        count = await db.patients.count_documents({})
        print(f"✓ Database test: {count} patients")
        
        client.close()
        
        # Update .env file
        env_content = """# MongoDB Configuration - LOCAL
MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3002

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
        
        ROOT_DIR = Path(__file__).parent
        with open(ROOT_DIR / '.env', 'w') as f:
            f.write(env_content)
        
        print("✓ .env updated")
        
        print("\n" + "=" * 50)
        print("✅ LOCAL DATABASE READY!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_local_db())