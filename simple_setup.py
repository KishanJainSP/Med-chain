#!/usr/bin/env python3
"""
Simple MedChain Setup - No Virtual Environment
Works directly with system Python installation
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"   ✅ Python {sys.version.split()[0]}")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip...")
    success, _ = run_command(f"{sys.executable} -m pip --version")
    if not success:
        print("   ❌ pip not available")
        return False
    print("   ✅ pip available")
    return True

def install_backend_deps():
    """Install backend dependencies"""
    print("🔧 Installing backend dependencies...")
    
    # Try requirements-minimal.txt first, then backend/requirements.txt
    requirements_files = ["requirements-minimal.txt", "backend/requirements.txt"]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"   📋 Using {req_file}")
            
            # Try normal install first
            success, output = run_command(f"{sys.executable} -m pip install -r {req_file}")
            if success:
                print("   ✅ Backend dependencies installed")
                return True
            
            # Try with --user flag
            print("   💡 Trying with --user flag...")
            success, output = run_command(f"{sys.executable} -m pip install --user -r {req_file}")
            if success:
                print("   ✅ Backend dependencies installed (user mode)")
                return True
            
            print(f"   ⚠️  Failed with {req_file}: {output}")
    
    print("   ❌ Could not install backend dependencies")
    print("   💡 Try running: pip install fastapi uvicorn motor pymongo python-dotenv")
    return False

def check_node():
    """Check Node.js"""
    print("📦 Checking Node.js...")
    success, output = run_command("node --version")
    if not success:
        print("   ❌ Node.js not found")
        print("   💡 Install from https://nodejs.org/")
        return False
    print(f"   ✅ Node.js {output.strip()}")
    return True

def install_frontend_deps():
    """Install frontend dependencies"""
    print("🎨 Installing frontend dependencies...")
    
    if not Path("frontend").exists():
        print("   ❌ Frontend directory not found")
        return False
    
    success, output = run_command("npm install")
    if not success:
        print(f"   ❌ npm install failed: {output}")
        return False
    
    print("   ✅ Frontend dependencies installed")
    return True

def create_env_files():
    """Create environment files"""
    print("⚙️  Creating configuration files...")
    
    # Backend .env
    backend_env = """MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local
HOST=0.0.0.0
PORT=8000
"""
    
    backend_env_path = Path("backend/.env")
    if not backend_env_path.exists():
        backend_env_path.write_text(backend_env)
        print("   ✅ Created backend/.env")
    
    # Frontend .env
    frontend_env = "REACT_APP_BACKEND_URL=http://localhost:8000\n"
    
    frontend_env_path = Path("frontend/.env")
    if not frontend_env_path.exists():
        frontend_env_path.write_text(frontend_env)
        print("   ✅ Created frontend/.env")

def check_mongodb():
    """Check MongoDB (optional)"""
    print("🗄️  Checking MongoDB...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        print("   ✅ MongoDB is running")
        return True
    except ImportError:
        print("   ⚠️  pymongo not installed yet")
        return True  # Will be installed with backend deps
    except Exception:
        print("   ⚠️  MongoDB not running (install and start MongoDB)")
        print("   💡 Download from https://www.mongodb.com/")
        return True  # Not critical for setup

def main():
    """Main setup function"""
    print("🏥 MedChain Simple Setup")
    print("=" * 30)
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    if not check_node():
        sys.exit(1)
    
    # Setup backend
    if not install_backend_deps():
        print("\n❌ Backend setup failed!")
        print("💡 Manual installation:")
        print("   pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests")
        sys.exit(1)
    
    # Setup frontend
    os.chdir("frontend")
    if not install_frontend_deps():
        os.chdir("..")
        sys.exit(1)
    os.chdir("..")
    
    # Create config files
    create_env_files()
    
    # Check MongoDB
    check_mongodb()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start MongoDB if not running")
    print("2. Run: python run.py")
    print("\nOptional (for AI chat):")
    print("- Install Ollama: https://ollama.ai/")
    print("- Run: ollama pull llama3.2")

if __name__ == "__main__":
    main()