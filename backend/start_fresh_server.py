#!/usr/bin/env python3
"""
Start fresh server with local MongoDB
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def kill_existing_servers():
    """Kill existing Python servers"""
    try:
        print("Stopping existing servers...")
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, shell=True)
        time.sleep(2)  # Wait for processes to stop
        print("✓ Existing servers stopped")
    except:
        print("✓ No existing servers to stop")

def start_server():
    """Start the FastAPI server"""
    
    print("=" * 50)
    print("Starting Fresh MedChain Server")
    print("=" * 50)
    
    # Kill existing servers first
    kill_existing_servers()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("Starting server with local MongoDB...")
    print("Database: medchain_local")
    print("CORS: Enabled for localhost:3002")
    print("URL: http://localhost:8000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'server:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
    except Exception as e:
        print(f"✗ Server error: {e}")

if __name__ == "__main__":
    start_server()