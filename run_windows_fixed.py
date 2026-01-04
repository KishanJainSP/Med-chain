#!/usr/bin/env python3
"""
MedChain Windows-Fixed Launcher
Handles Windows PATH issues with npm/Node.js
"""

import os
import sys
import subprocess
import time
import signal
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

def get_windows_paths():
    """Get comprehensive Windows PATH including npm locations"""
    paths = []
    
    # Get current PATH
    current_path = os.environ.get('PATH', '').split(os.pathsep)
    paths.extend(current_path)
    
    # Add common Node.js/npm locations
    common_locations = [
        # User AppData locations
        os.path.expanduser("~/AppData/Roaming/npm"),
        os.path.expanduser("~/AppData/Local/npm"),
        
        # Program Files locations
        "C:/Program Files/nodejs",
        "C:/Program Files (x86)/nodejs",
        
        # Chocolatey locations
        "C:/ProgramData/chocolatey/lib/nodejs/tools",
        "C:/tools/nodejs",
        
        # NVM locations
        os.path.expanduser("~/AppData/Roaming/nvm"),
        
        # Yarn global locations
        os.path.expanduser("~/AppData/Local/Yarn/bin"),
        os.path.expanduser("~/AppData/Roaming/npm"),
    ]
    
    # Add locations that exist
    for location in common_locations:
        if os.path.exists(location) and location not in paths:
            paths.append(location)
    
    return os.pathsep.join(paths)

def find_npm_executable():
    """Find npm executable with comprehensive Windows search"""
    print("🔍 Searching for npm...")
    
    # Get enhanced PATH
    enhanced_path = get_windows_paths()
    
    # Possible npm executable names
    npm_names = ["npm.cmd", "npm.exe", "npm", "yarn.cmd", "yarn.exe", "yarn"]
    
    # Search in PATH
    for path_dir in enhanced_path.split(os.pathsep):
        if not path_dir or not os.path.exists(path_dir):
            continue
            
        for npm_name in npm_names:
            npm_path = os.path.join(path_dir, npm_name)
            if os.path.isfile(npm_path):
                # Test if it works
                try:
                    result = subprocess.run([npm_path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"   ✅ Found working npm: {npm_path}")
                        return npm_path
                except:
                    continue
    
    # Direct search in common locations
    direct_paths = [
        "C:/Program Files/nodejs/npm.cmd",
        "C:/Program Files (x86)/nodejs/npm.cmd",
        os.path.expanduser("~/AppData/Roaming/npm/npm.cmd"),
        "C:/ProgramData/chocolatey/lib/nodejs/tools/npm.cmd",
    ]
    
    for npm_path in direct_paths:
        if os.path.isfile(npm_path):
            try:
                result = subprocess.run([npm_path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   ✅ Found npm at: {npm_path}")
                    return npm_path
            except:
                continue
    
    print("   ❌ npm not found in any location")
    return None

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi, uvicorn, motor, pymongo
        print("   ✅ Backend dependencies found")
    except ImportError as e:
        print(f"   ❌ Missing backend dependency: {e}")
        print("   💡 Run: python setup.py")
        return False, None
    
    # Find npm
    npm_path = find_npm_executable()
    
    if npm_path:
        # Check if frontend dependencies are installed
        if not (FRONTEND_DIR / "node_modules").exists():
            print("   ⚠️  Frontend dependencies not installed")
            print("   Installing frontend dependencies...")
            try:
                # Use enhanced PATH for npm install
                env = os.environ.copy()
                env['PATH'] = get_windows_paths()
                
                result = subprocess.run([npm_path, "install"], cwd=FRONTEND_DIR, 
                                      capture_output=True, text=True, timeout=300, env=env)
                if result.returncode == 0:
                    print("   ✅ Frontend dependencies installed")
                else:
                    print(f"   ❌ npm install failed: {result.stderr}")
                    return True, None  # Backend still works
            except Exception as e:
                print(f"   ❌ npm install error: {e}")
                return True, None  # Backend still works
        else:
            print("   ✅ Frontend dependencies found")
    else:
        print("   ⚠️  npm not found - frontend will not be available")
        print("   💡 Install Node.js from https://nodejs.org/")
    
    return True, npm_path

def start_backend(manager):
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR.absolute())
    
    try:
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
        
    except Exception as e:
        print(f"   ❌ Backend startup error: {e}")
        return False

def start_frontend(manager, npm_path):
    """Start the frontend server"""
    if not npm_path:
        print("   ⚠️  Skipping frontend - npm not available")
        return False
    
    print("🚀 Starting frontend server...")
    
    try:
        # Use enhanced PATH
        env = os.environ.copy()
        env["REACT_APP_BACKEND_URL"] = f"http://localhost:{BACKEND_PORT}"
        env['PATH'] = get_windows_paths()
        
        # Use the npm path we found
        process = subprocess.Popen([npm_path, "start"], cwd=FRONTEND_DIR, env=env)
        
        manager.add_process(process, "Frontend")
        
        # Wait for frontend to start
        import requests
        for i in range(60):
            try:
                response = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=1)
                if response.status_code == 200:
                    print(f"   ✅ Frontend running at http://localhost:{FRONTEND_PORT}")
                    return True
            except:
                time.sleep(2)
        
        print("   ❌ Frontend failed to start")
        return False
        
    except Exception as e:
        print(f"   ❌ Frontend startup error: {e}")
        return False

def start_backend_only():
    """Start only backend (fallback mode)"""
    print("🚀 Starting backend-only mode...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR.absolute())
    
    try:
        # Start backend without reload for stability
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "server:app",
            "--host", "0.0.0.0",
            "--port", str(BACKEND_PORT)
        ], cwd=BACKEND_DIR, env=env)
        
        # Wait for backend to start
        import requests
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{BACKEND_PORT}/docs", timeout=1)
                if response.status_code == 200:
                    print(f"   ✅ Backend running at http://localhost:{BACKEND_PORT}")
                    print(f"   📖 API Documentation: http://localhost:{BACKEND_PORT}/docs")
                    print(f"   💡 Install Node.js for frontend features")
                    
                    print("\n🎯 Backend-only mode active!")
                    print("   All API endpoints are available")
                    print("   Use the API docs to interact with the system")
                    print("   Press Ctrl+C to stop")
                    
                    # Keep running
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print("\n🛑 Stopping backend...")
                        process.terminate()
                        process.wait()
                    
                    return True
            except:
                time.sleep(1)
        
        print("   ❌ Backend failed to start")
        return False
        
    except Exception as e:
        print(f"   ❌ Backend startup error: {e}")
        return False

def main():
    """Main application launcher"""
    print("🏥 MedChain Windows-Fixed Launcher")
    print("=" * 40)
    
    # Check dependencies
    deps_ok, npm_path = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Backend dependencies missing!")
        print("💡 Run: python setup.py")
        sys.exit(1)
    
    # If no npm, offer backend-only mode
    if not npm_path:
        print("\n⚠️  Frontend not available (npm not found)")
        print("💡 Options:")
        print("1. Install Node.js from https://nodejs.org/")
        print("2. Continue with backend-only mode")
        
        choice = input("\nContinue with backend-only? (y/N): ").lower()
        if choice == 'y':
            start_backend_only()
            return
        else:
            print("Install Node.js and try again!")
            sys.exit(1)
    
    # Create process manager
    manager = ProcessManager()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start backend
        if not start_backend(manager):
            print("\n❌ Backend failed to start!")
            manager.cleanup()
            sys.exit(1)
        
        # Start frontend
        frontend_started = start_frontend(manager, npm_path)
        
        if frontend_started:
            print("\n🎉 MedChain is running!")
            print(f"   Frontend: http://localhost:{FRONTEND_PORT}")
            print(f"   Backend API: http://localhost:{BACKEND_PORT}")
            print(f"   API Docs: http://localhost:{BACKEND_PORT}/docs")
        else:
            print("\n⚠️  Frontend failed to start!")
            print("🎯 Backend-only mode active!")
            print(f"   Backend API: http://localhost:{BACKEND_PORT}")
            print(f"   API Docs: http://localhost:{BACKEND_PORT}/docs")
        
        print("\n   Press Ctrl+C to stop all services")
        
        # Keep running
        while manager.running:
            time.sleep(1)
            
            # Check if backend is still running (critical)
            for process, name in manager.processes:
                if name == "Backend" and process.poll() is not None:
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