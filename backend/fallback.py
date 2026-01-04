"""
Fallback persistence system for wallet registrations when MongoDB is unavailable.
Implements in-memory queue with JSON file backup and async retry mechanism.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
import threading
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class PendingWalletRegistration:
    """Data structure for pending wallet registrations"""
    id: str
    wallet_address: str
    user_type: str  # 'institution', 'doctor', 'patient'
    data: Dict[str, Any]
    timestamp: float
    retry_count: int = 0
    max_retries: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PendingWalletRegistration':
        return cls(**data)

class FallbackPersistence:
    """
    Fallback system for wallet registrations with:
    - In-memory queue for fast access
    - JSON file backup for persistence across restarts
    - Async retry mechanism with exponential backoff
    - Thread-safe operations
    """
    
    def __init__(self, backup_file: str = "pending_registrations.json"):
        self.backup_file = Path(__file__).parent / backup_file
        self.pending_registrations: Dict[str, PendingWalletRegistration] = {}
        self.lock = threading.RLock()
        self.retry_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Load existing pending registrations
        self._load_from_file()
        
        logger.info(f"FallbackPersistence initialized with {len(self.pending_registrations)} pending registrations")
    
    def _load_from_file(self):
        """Load pending registrations from backup file"""
        try:
            if self.backup_file.exists():
                with open(self.backup_file, 'r') as f:
                    data = json.load(f)
                    
                for reg_data in data.get('registrations', []):
                    reg = PendingWalletRegistration.from_dict(reg_data)
                    self.pending_registrations[reg.id] = reg
                    
                logger.info(f"Loaded {len(self.pending_registrations)} pending registrations from backup")
        except Exception as e:
            logger.error(f"Failed to load pending registrations: {e}")
    
    def _save_to_file(self):
        """Save pending registrations to backup file"""
        try:
            with self.lock:
                data = {
                    'timestamp': time.time(),
                    'registrations': [reg.to_dict() for reg in self.pending_registrations.values()]
                }
                
                # Atomic write using temporary file
                temp_file = self.backup_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                temp_file.replace(self.backup_file)
                logger.debug(f"Saved {len(self.pending_registrations)} pending registrations to backup")
                
        except Exception as e:
            logger.error(f"Failed to save pending registrations: {e}")
    
    def add_pending_registration(
        self, 
        wallet_address: str, 
        user_type: str, 
        data: Dict[str, Any]
    ) -> str:
        """Add a new pending wallet registration"""
        with self.lock:
            registration_id = str(uuid.uuid4())
            
            pending_reg = PendingWalletRegistration(
                id=registration_id,
                wallet_address=wallet_address.lower(),
                user_type=user_type,
                data=data,
                timestamp=time.time()
            )
            
            self.pending_registrations[registration_id] = pending_reg
            self._save_to_file()
            
            logger.info(f"Added pending {user_type} registration for wallet {wallet_address}")
            return registration_id
    
    def get_pending_registration(self, registration_id: str) -> Optional[PendingWalletRegistration]:
        """Get a pending registration by ID"""
        with self.lock:
            return self.pending_registrations.get(registration_id)
    
    def remove_pending_registration(self, registration_id: str) -> bool:
        """Remove a pending registration (after successful sync)"""
        with self.lock:
            if registration_id in self.pending_registrations:
                del self.pending_registrations[registration_id]
                self._save_to_file()
                logger.info(f"Removed pending registration {registration_id}")
                return True
            return False
    
    def get_all_pending(self) -> List[PendingWalletRegistration]:
        """Get all pending registrations"""
        with self.lock:
            return list(self.pending_registrations.values())
    
    def increment_retry_count(self, registration_id: str) -> bool:
        """Increment retry count for a registration"""
        with self.lock:
            if registration_id in self.pending_registrations:
                reg = self.pending_registrations[registration_id]
                reg.retry_count += 1
                
                if reg.retry_count >= reg.max_retries:
                    logger.warning(f"Registration {registration_id} exceeded max retries, removing")
                    del self.pending_registrations[registration_id]
                    self._save_to_file()
                    return False
                
                self._save_to_file()
                return True
            return False
    
    async def start_retry_worker(self, db_manager):
        """Start the async retry worker"""
        if self.is_running:
            return
        
        self.is_running = True
        self.retry_task = asyncio.create_task(self._retry_worker(db_manager))
        logger.info("Fallback retry worker started")
    
    async def stop_retry_worker(self):
        """Stop the async retry worker"""
        self.is_running = False
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
        logger.info("Fallback retry worker stopped")
    
    async def _retry_worker(self, db_manager):
        """Background worker to retry pending registrations"""
        while self.is_running:
            try:
                await self._process_pending_registrations(db_manager)
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry worker: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_pending_registrations(self, db_manager):
        """Process all pending registrations"""
        pending_regs = self.get_all_pending()
        
        if not pending_regs:
            return
        
        logger.info(f"Processing {len(pending_regs)} pending registrations")
        
        # Check if database is available
        db = await db_manager.get_database()
        if not db:
            logger.debug("Database not available, skipping retry")
            return
        
        for reg in pending_regs:
            try:
                success = await self._retry_single_registration(db, reg)
                if success:
                    self.remove_pending_registration(reg.id)
                    logger.info(f"Successfully synced pending registration {reg.id}")
                else:
                    if not self.increment_retry_count(reg.id):
                        logger.error(f"Registration {reg.id} failed permanently")
                
            except Exception as e:
                logger.error(f"Error processing registration {reg.id}: {e}")
                self.increment_retry_count(reg.id)
    
    async def _retry_single_registration(
        self, 
        db, 
        reg: PendingWalletRegistration
    ) -> bool:
        """Retry a single registration"""
        try:
            collection_name = f"{reg.user_type}s"  # institutions, doctors, patients
            
            # Check if already exists
            existing = await db[collection_name].find_one(
                {"wallet_address": reg.wallet_address}, 
                {"_id": 0}
            )
            
            if existing:
                logger.info(f"Registration {reg.id} already exists in database")
                return True
            
            # Insert the registration
            doc = reg.data.copy()
            doc['created_at'] = datetime.fromtimestamp(reg.timestamp, timezone.utc).isoformat()
            
            await db[collection_name].insert_one(doc)
            logger.info(f"Successfully inserted {reg.user_type} registration for {reg.wallet_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry registration {reg.id}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get fallback system status"""
        with self.lock:
            return {
                "pending_count": len(self.pending_registrations),
                "is_running": self.is_running,
                "backup_file": str(self.backup_file),
                "backup_exists": self.backup_file.exists(),
                "pending_by_type": {
                    user_type: len([r for r in self.pending_registrations.values() if r.user_type == user_type])
                    for user_type in ['institution', 'doctor', 'patient']
                }
            }

# Global fallback persistence instance
fallback_persistence = FallbackPersistence()