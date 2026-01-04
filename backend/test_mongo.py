#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mongo():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        print(f"Connecting to: {mongo_url}")
        print(f"Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        result = await db.institutions.find({}, {"_id": 0}).to_list(1)
        print(f"Connection successful! Found {len(result)} institutions")
        
        client.close()
        
    except Exception as e:
        print(f"MongoDB connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())