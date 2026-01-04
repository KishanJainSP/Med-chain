"""
Production-grade MongoDB connection manager with singleton pattern,
automatic reconnection, health checks, and circuit breaker functionality.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
import os
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Singleton MongoDB connection manager with:
    - Persistent connection pooling
    - Automatic reconnection with exponential backoff
    - Health checks before operations
    - Circuit breaker pattern
    - Graceful error handling
    """
    
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    _connection_lock = asyncio.Lock()
    _last_health_check = 0
    _health_check_interval = 30  # seconds
    _is_healthy = False
    _circuit_breaker_failures = 0
    _circuit_breaker_threshold = 5
    _circuit_breaker_reset_time = 60  # seconds
    _last_failure_time = 0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            self.db_name = os.environ.get('DB_NAME', 'medchain')
            self._initialized = True
            logger.info(f"DatabaseManager initialized with URL: {self.mongo_url}")
    
    async def _create_connection(self) -> bool:
        """Create new MongoDB connection with proper configuration"""
        try:
            if self._client:
                self._client.close()
            
            # Production-grade connection settings
            self._client = AsyncIOMotorClient(
                self.mongo_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=20000,          # 20 second socket timeout
                maxPoolSize=50,                 # Connection pool size
                minPoolSize=5,                  # Minimum connections
                maxIdleTimeMS=30000,           # 30 second idle timeout
                retryWrites=True,              # Enable retry writes
                retryReads=True,               # Enable retry reads
                w='majority',                  # Write concern
                j=True                         # Journal writes
            )
            
            # Test connection
            await self._client.admin.command('ping')
            self._database = self._client[self.db_name]
            
            # Reset circuit breaker on successful connection
            self._circuit_breaker_failures = 0
            self._is_healthy = True
            self._last_health_check = time.time()
            
            logger.info("MongoDB connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB connection: {e}")
            self._is_healthy = False
            self._circuit_breaker_failures += 1
            self._last_failure_time = time.time()
            return False
    
    async def _health_check(self) -> bool:
        """Perform health check on existing connection"""
        if not self._client or not self._database:
            return False
        
        try:
            # Quick ping to check connection
            await self._client.admin.command('ping', maxTimeMS=3000)
            self._is_healthy = True
            self._last_health_check = time.time()
            return True
            
        except Exception as e:
            logger.warning(f"MongoDB health check failed: {e}")
            self._is_healthy = False
            return False
    
    async def _should_attempt_connection(self) -> bool:
        """Circuit breaker logic - should we attempt connection?"""
        if self._circuit_breaker_failures < self._circuit_breaker_threshold:
            return True
        
        # Check if enough time has passed to reset circuit breaker
        if time.time() - self._last_failure_time > self._circuit_breaker_reset_time:
            logger.info("Circuit breaker reset - attempting reconnection")
            self._circuit_breaker_failures = 0
            return True
        
        return False
    
    async def connect(self) -> bool:
        """Initialize database connection with retry logic"""
        async with self._connection_lock:
            if self._is_healthy and self._client and self._database:
                return True
            
            if not await self._should_attempt_connection():
                logger.warning("Circuit breaker open - skipping connection attempt")
                return False
            
            max_retries = 3
            base_delay = 1
            
            for attempt in range(max_retries):
                if await self._create_connection():
                    return True
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying connection in {delay} seconds (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
            
            logger.error("Failed to establish MongoDB connection after all retries")
            return False
    
    async def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance with health check"""
        # Check if we need a health check
        current_time = time.time()
        if (current_time - self._last_health_check) > self._health_check_interval:
            if not await self._health_check():
                logger.info("Health check failed - attempting reconnection")
                await self.connect()
        
        if self._is_healthy and self._database:
            return self._database
        
        # Try to reconnect if not healthy
        if await self.connect():
            return self._database
        
        return None
    
    async def is_connected(self) -> bool:
        """Check if database is connected and healthy"""
        if not self._is_healthy or not self._client or not self._database:
            return False
        
        # Perform quick health check if needed
        current_time = time.time()
        if (current_time - self._last_health_check) > self._health_check_interval:
            return await self._health_check()
        
        return True
    
    async def reconnect(self) -> bool:
        """Force reconnection to database"""
        logger.info("Forcing database reconnection")
        self._is_healthy = False
        return await self.connect()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status for monitoring"""
        return {
            "connected": self._is_healthy,
            "client_exists": self._client is not None,
            "database_exists": self._database is not None,
            "last_health_check": self._last_health_check,
            "circuit_breaker_failures": self._circuit_breaker_failures,
            "circuit_breaker_open": self._circuit_breaker_failures >= self._circuit_breaker_threshold,
            "mongo_url": self.mongo_url.replace(self.mongo_url.split('@')[-1] if '@' in self.mongo_url else '', '***') if self.mongo_url else None,
            "database_name": self.db_name
        }
    
    async def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._is_healthy = False
            logger.info("MongoDB connection closed")

# Global database manager instance
db_manager = DatabaseManager()

@asynccontextmanager
async def get_db_context():
    """Context manager for database operations with automatic error handling"""
    db = await db_manager.get_database()
    if db is None:
        raise ConnectionFailure("Database not available")
    
    try:
        yield db
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        # Mark as unhealthy to trigger reconnection on next request
        db_manager._is_healthy = False
        raise

async def get_db() -> Optional[AsyncIOMotorDatabase]:
    """FastAPI dependency for database access"""
    return await db_manager.get_database()

async def ensure_db_connection() -> bool:
    """Ensure database connection is established"""
    return await db_manager.connect()

async def get_db_health() -> Dict[str, Any]:
    """Get database health status"""
    is_connected = await db_manager.is_connected()
    status = db_manager.get_connection_status()
    
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "details": status,
        "timestamp": time.time()
    }