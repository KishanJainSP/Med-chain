#!/usr/bin/env python3
"""
MedChain Production Launcher - Windows Fixed
Single command to run the entire application with Windows npm path fixes
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

def find_npm_command():
    """Find the correct npm command on Windows"""
    npm_commands = []
    
    if os.name == 'nt':  # Windows
        # Common npm locations on Windows
        npm_commands = [
            "npm.cmd",
            "npm",
            "npx.cmd", 
            str(Path(os.environ.get("APPDATA", "")) / "npm" / "npm.cmd"),
            str(Path(os.environ.get("ProgramFiles", "")) / "nodejs" / "npm.cmd"),
            str(Path(os.environ.get("ProgramFiles(x86)", "")) / "nodejs" / "npm.cmd"),
        ]
    else:
        npm_commands = ["npm", "yarn"]
    
    for cmd in npm_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ Found npm: {cmd}")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    return None

def find_node_command():
    """Find the correct node command"""
    node_commands = []
    
    if os.name == 'nt':  # Windows
        node_commands = [
            "node.exe",
            "node",
            str(Path(os.environ.get("ProgramFiles", "")) / "nodejs" / "node.exe"),
            str(Path(os.environ.get("ProgramFiles(x86)", "")) / "nodejs" / "node.exe"),
        ]
    else:
        node_commands = ["node", "nodejs"]
    
    for cmd in node_commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ Found Node.js: {cmd} {result.stdout.strip()}")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
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
        print("   💡 Run setup first: python setup.py")
        return False
    
    # Check Node.js
    node_cmd = find_node_command()
    if not node_cmd:
        print("   ❌ Node.js not found")
        print("   💡 Install Node.js from https://nodejs.org/")
        print("   💡 Make sure to check 'Add to PATH' during installation")
        return False
    
    # Check npm
    npm_cmd = find_npm_command()
    if not npm_cmd:
        print("   ❌ npm not found")
        print("   💡 Reinstall Node.js from https://nodejs.org/")
        print("   💡 Make sure to check 'Add to PATH' during installation")
        return False
    
    # Store npm command for later use
    global NPM_COMMAND
    NPM_COMMAND = npm_cmd
    
    # Check if frontend dependencies are installed
    if not (FRONTEND_DIR / "node_modules").exists():
        print("   ⚠️  Frontend dependencies not installed")
        print("   Installing frontend dependencies...")
        try:
            result = subprocess.run([npm_cmd, "install"], cwd=FRONTEND_DIR, 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("   ✅ Frontend dependencies installed")
            else:
                print(f"   ❌ npm install failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("   ❌ npm install timed out")
            return False
        except Exception as e:
            print(f"   ❌ npm install error: {e}")
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
        print("   ⚠️  MongoDB not running")
        print("   💡 The app will work with limited features")
        print("   💡 Install MongoDB from https://www.mongodb.com/ for full features")
        return True  # Don't fail, just warn

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
                print("   💡 Run: ollama pull llama3.2")
        else:
            raise Exception("Ollama not responding")
    except Exception:
        print("   ⚠️  Ollama not available (chat features will be limited)")
        print("   💡 Install from https://ollama.ai/ for full AI features")

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

def start_frontend(manager):
    """Start the frontend server"""
    print("🚀 Starting frontend server...")
    
    # Set environment variable for backend URL
    env = os.environ.copy()
    env["REACT_APP_BACKEND_URL"] = f"http://localhost:{BACKEND_PORT}"
    
    try:
        # Use the npm command we found earlier
        process = subprocess.Popen([
            NPM_COMMAND, "start"
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
        
    except Exception as e:
        print(f"   ❌ Frontend startup error: {e}")
        return False

def start_backend_only():
    """Start only the backend server (fallback mode)"""
    print("🚀 Starting backend-only mode...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR.absolute())
    
    try:
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
                    print(f"   💡 Frontend not available - install Node.js for full features")
                    
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
    print("🏥 MedChain Application Launcher")
    print("=" * 40)
    
    # Check all dependencies
    deps_ok = check_dependencies()
    
    # Always check MongoDB and Ollama (non-critical)
    check_mongodb()
    check_ollama()
    
    if not deps_ok:
        print("\n❌ Dependencies missing!")
        print("💡 Try running: python setup.py")
        
        # Check if we can at least run backend
        try:
            import fastapi, uvicorn
            print("\n🔄 Attempting backend-only mode...")
            if start_backend_only():
                return
        except ImportError:
            pass
        
        sys.exit(1)
    
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
            print("\n❌ Backend failed to start!")
            manager.cleanup()
            sys.exit(1)
        
        # Start frontend
        if not start_frontend(manager):
            print("\n⚠️  Frontend failed to start!")
            print("💡 Backend is running - you can use the API directly")
            print(f"   API Docs: http://localhost:{BACKEND_PORT}/docs")
            
            # Continue with backend only
            print("\n🔄 Continuing in backend-only mode...")
            print("   Press Ctrl+C to stop")
        else:
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
                    if name == "Backend":
                        # Backend is critical
                        manager.cleanup()
                        sys.exit(1)
                    else:
                        # Frontend failure is not critical
                        print(f"   🔄 Continuing without {name}")
    
    except KeyboardInterrupt:
        manager.cleanup()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        manager.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()