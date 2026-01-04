#!/usr/bin/env python3
"""
MedChain Production Launcher
Single command to run the entire application
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
BACKEND_DIR = Path("backend")
FRONTEND_DIR = Path("frontend")

class ProcessManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def add_process(self, process, name):
        self.processes.append((process, name))
        
    def cleanup(self):
        print("\n🛑 Shutting down MedChain...")
        self.running = False
        for process, name in self.processes:
            if process.poll() is None:
                print(f"   Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ All processes stopped")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi, uvicorn, motor, pymongo
        print("   ✅ Backend dependencies found")
    except ImportError as e:
        print(f"   ❌ Missing backend dependency: {e}")
        print("   Run: pip install -r backend/requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js found: {result.stdout.strip()}")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("   ❌ Node.js not found")
        print("   Please install Node.js from https://nodejs.org/")
        return False
    
    # Check if frontend dependencies are installed
    if not (FRONTEND_DIR / "node_modules").exists():
        print("   ⚠️  Frontend dependencies not installed")
        print("   Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
            print("   ✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install frontend dependencies")
            return False
    else:
        print("   ✅ Frontend dependencies found")
    
    return True

def check_mongodb():
    """Check if MongoDB is running"""
    print("🔍 Checking MongoDB...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        print("   ✅ MongoDB is running")
        return True
    except Exception:
        print("   ❌ MongoDB not running")
        print("   Please start MongoDB or install it from https://www.mongodb.com/")
        return False

def check_ollama():
    """Check if Ollama is available (optional)"""
    print("🔍 Checking Ollama (optional)...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"   ✅ Ollama running with {len(models)} models")
            else:
                print("   ⚠️  Ollama running but no models installed")
                print("   Run: ollama pull llama3.2")
        else:
            raise Exception("Ollama not responding")
    except Exception:
        print("   ⚠️  Ollama not available (chat features will be limited)")
        print("   Install from https://ollama.ai/ for full AI features")

def start_backend(manager):
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    # Use current Python environment (no virtual environment)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR.absolute())
    
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "server:app",
        "--host", "0.0.0.0",
        "--port", str(BACKEND_PORT),
        "--reload"
    ], cwd=BACKEND_DIR, env=env)
    
    manager.add_process(process, "Backend")
    
    # Wait for backend to start
    import requests
    for i in range(30):
        try:
            response = requests.get(f"http://localhost:{BACKEND_PORT}/docs", timeout=1)
            if response.status_code == 200:
                print(f"   ✅ Backend running at http://localhost:{BACKEND_PORT}")
                return True
        except:
            time.sleep(1)
    
    print("   ❌ Backend failed to start")
    return False

def start_frontend(manager):
    """Start the frontend server"""
    print("🚀 Starting frontend server...")
    
    # Set environment variable for backend URL
    env = os.environ.copy()
    env["REACT_APP_BACKEND_URL"] = f"http://localhost:{BACKEND_PORT}"
    
    process = subprocess.Popen([
        "npm", "start"
    ], cwd=FRONTEND_DIR, env=env)
    
    manager.add_process(process, "Frontend")
    
    # Wait for frontend to start
    import requests
    for i in range(60):  # Frontend takes longer to start
        try:
            response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=1)
            if response.status_code == 200:
                print(f"   ✅ Frontend running at http://localhost:{FRONTEND_PORT}")
                return True
        except:
            time.sleep(2)
    
    print("   ❌ Frontend failed to start")
    return False

def main():
    """Main application launcher"""
    print("🏥 MedChain Application Launcher")
    print("=" * 40)
    
    # Check all dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_mongodb():
        sys.exit(1)
    
    check_ollama()  # Optional
    
    # Create process manager
    manager = ProcessManager()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start backend
        if not start_backend(manager):
            manager.cleanup()
            sys.exit(1)
        
        # Start frontend
        if not start_frontend(manager):
            manager.cleanup()
            sys.exit(1)
        
        print("\n🎉 MedChain is running!")
        print(f"   Frontend: http://localhost:{FRONTEND_PORT}")
        print(f"   Backend API: http://localhost:{BACKEND_PORT}")
        print(f"   API Docs: http://localhost:{BACKEND_PORT}/docs")
        print("\n   Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        while manager.running:
            time.sleep(1)
            
            # Check if processes are still running
            for process, name in manager.processes:
                if process.poll() is not None:
                    print(f"   ❌ {name} stopped unexpectedly")
                    manager.cleanup()
                    sys.exit(1)
    
    except KeyboardInterrupt:
        manager.cleanup()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        manager.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()